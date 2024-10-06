import os
import uuid

from datetime import datetime
from dateutil.parser import parse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser

from settings import settings
from .minio import MinioStorage
from server_software.serializers import *
from .auth import AuthBySessionID, AuthBySessionIDIfExists, IsAuth, IsManagerAuth
from .redis import session_storage
from .services import get_or_create_user_cart, is_valid_versions, \
    calculate_total_installing_time_for_req, add_item_to_request

SINGLETON_USER = User(id=1, username="admin")
SINGLETON_MANAGER = User(id=2, username="manager")


# Software

@swagger_auto_schema(method='get', responses={
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'software': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
            'install_software_request_id': openapi.Schema(type=openapi.TYPE_NUMBER),
            'items_in_cart': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    status.HTTP_403_FORBIDDEN: "Forbidden",
})
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([AuthBySessionIDIfExists])
def get_software_list(request):
    """
    Получение списка ПО
    """
    user = request.user
    software_title = request.query_params.get("software_title", "")
    software_list = Software.objects.filter(title__istartswith=software_title, is_active=True)

    req = None
    items_in_cart = 0

    if user is not None:
        req = InstallSoftwareRequest.objects.filter(client_id=user.pk,
                                                    status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
        if req is not None:
            items_in_cart = SoftwareInRequest.objects.filter(request_id=req.id).count()

    serializer = SoftwareSerializer(software_list, many=True)
    return Response(
        {
            "software": serializer.data,
            "install_software_request_id": req.id if req else None,
            "items_in_cart": items_in_cart,
        },
        status=status.HTTP_200_OK)


@swagger_auto_schema(method='post',
                     request_body=SoftwareSerializer,
                     responses={
                         status.HTTP_200_OK: SoftwareSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                     })
@api_view(['POST'])
@permission_classes([IsManagerAuth])
def post_software(request):
    """
    Добавление ПО
    """
    serializer = SoftwareSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_software = serializer.save()
    serializer = SoftwareSerializer(new_software)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="post",
                     manual_parameters=[
                         openapi.Parameter(name="image",
                                           in_=openapi.IN_QUERY,
                                           type=openapi.TYPE_FILE,
                                           required=True, description="Image")],
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                     })
@api_view(['POST'])
@permission_classes([IsManagerAuth])
def post_software_image(request, pk):
    """
    Загрузка изображения ПО в Minio
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)

    minio_storage = MinioStorage(endpoint=settings.MINIO_ENDPOINT_URL,
                                 access_key=settings.MINIO_ACCESS_KEY,
                                 secret_key=settings.MINIO_SECRET_KEY,
                                 secure=settings.MINIO_SECURE)

    file = request.FILES.get("image")
    if not file:
        return Response("No image in request", status=status.HTTP_400_BAD_REQUEST)

    file_extension = os.path.splitext(file.name)[1]
    file_name = f"{pk}{file_extension}"

    try:
        minio_storage.load_file(settings.MINIO_BUCKET_NAME, file_name, file)
    except Exception as e:
        return Response(f"Failed to load image: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    software.logo_file_path = f"http://{settings.MINIO_ENDPOINT_URL}/{settings.MINIO_BUCKET_NAME}/{file_name}"
    software.save()
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='get',
                     responses={
                         status.HTTP_200_OK: SoftwareSerializer(),
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['GET'])
@permission_classes([AllowAny])
def get_software(request, pk):
    """
    Получение ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    serialized_software = SoftwareSerializer(software)
    return Response(serialized_software.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete',
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['DELETE'])
@permission_classes([IsManagerAuth])
def delete_software(request, pk):
    """
    Удаление ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)

    if software.logo_file_path != "":
        minio_storage = MinioStorage(endpoint=settings.MINIO_ENDPOINT_URL,
                                     access_key=settings.MINIO_ACCESS_KEY,
                                     secret_key=settings.MINIO_SECRET_KEY,
                                     secure=settings.MINIO_SECURE)
        file_extension = os.path.splitext(software.logo_file_path)[1]
        file_name = f"{pk}{file_extension}"
        try:
            minio_storage.delete_file(settings.MINIO_BUCKET_NAME, file_name)
        except Exception as e:
            return Response(f"Failed to delete image: {e}",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        software.logo_file_path = ""

    software.is_active = False
    software.save()
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='put',
                     request_body=SoftwareSerializer,
                     responses={
                         status.HTTP_200_OK: SoftwareSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['PUT'])
@permission_classes([IsManagerAuth])
def put_software(request, pk):
    """
    Изменение ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)

    serializer = SoftwareSerializer(software, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post',
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['POST'])
@permission_classes([IsAuth])
@authentication_classes([AuthBySessionID])
def post_software_to_request(request, pk):
    """
    Добавление ПО в заявку на установку
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    request_id = get_or_create_user_cart(request.user.id)
    add_item_to_request(request_id, pk)
    return Response(status=status.HTTP_200_OK)


# InstallSoftwareRequest

# TODO: права
@swagger_auto_schema(method='get',
                     responses={
                         status.HTTP_200_OK: SoftwareSerializer(many=True),
                     })
@api_view(['GET'])
def get_install_software_requests(request):
    """
    Получение списка заявок на установку ПО
    """
    status_filter = request.query_params.get("status")
    formation_datetime_start_filter = request.query_params.get("formation_start")
    formation_datetime_end_filter = request.query_params.get("formation_end")

    filters = ~Q(status=InstallSoftwareRequest.RequestStatus.DELETED)
    if status_filter is not None:
        filters &= Q(status=status_filter.upper())
    if formation_datetime_start_filter is not None:
        filters &= Q(formation_datetime__gte=parse(formation_datetime_start_filter))
    if formation_datetime_end_filter is not None:
        filters &= Q(formation_datetime__lte=parse(formation_datetime_end_filter))

    install_software_requests = InstallSoftwareRequest.objects.filter(filters).select_related("client")
    serializer = InstallSoftwareRequestSerializer(install_software_requests, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# TODO: права
@swagger_auto_schema(method='get',
                     responses={
                         status.HTTP_200_OK: FullInstallSoftwareRequestSerializer(),
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['GET'])
def get_install_software_request(request, pk):
    """
    Получение заявки на установку ПО
    """
    filters = Q(id=pk) & ~Q(status=InstallSoftwareRequest.RequestStatus.DELETED)
    install_software_request = InstallSoftwareRequest.objects.filter(filters).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    serializer = FullInstallSoftwareRequestSerializer(install_software_request)
    return Response(serializer.data, status=status.HTTP_200_OK)


# TODO: права
@swagger_auto_schema(method='put',
                     request_body=PutInstallSoftwareRequestSerializer,
                     responses={
                         status.HTTP_200_OK: PutInstallSoftwareRequestSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['PUT'])
def put_install_software_request(request, pk):
    """
    Изменение заявки на установку ПО
    """
    install_software_request = InstallSoftwareRequest.objects.filter(id=pk,
                                                                     status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    serializer = PutInstallSoftwareRequestSerializer(install_software_request,
                                                     data=request.data,
                                                     partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: права
@swagger_auto_schema(method='put',
                     responses={
                         status.HTTP_200_OK: InstallSoftwareRequestSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['PUT'])
def form_install_software_request(request, pk):
    """
    Формирование заявки на установку ПО
    """
    install_software_request = InstallSoftwareRequest.objects.filter(id=pk,
                                                                     status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    if install_software_request.host is None or install_software_request.host == "":
        return Response("InstallSoftwareRequest.host is empty", status=status.HTTP_400_BAD_REQUEST)

    if not is_valid_versions(pk):
        return Response("One or more software versions is empty", status=status.HTTP_400_BAD_REQUEST)

    install_software_request.status = InstallSoftwareRequest.RequestStatus.FORMED
    install_software_request.formation_datetime = datetime.now()
    install_software_request.save()
    serializer = InstallSoftwareRequestSerializer(install_software_request)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='put',
                     responses={
                         status.HTTP_200_OK: InstallSoftwareRequestSerializer(),
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['PUT'])
@permission_classes([IsManagerAuth])
@authentication_classes([AuthBySessionID])
def resolve_install_software_request(request, pk):
    """
    Закрытие заявки на установку ПО модератором
    """
    install_software_request = InstallSoftwareRequest.objects.filter(id=pk,
                                                                     status=InstallSoftwareRequest.RequestStatus.FORMED).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    serializer = ResolveInstallSoftwareRequestSerializer(install_software_request,
                                                         data=request.data,
                                                         partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    install_software_request = InstallSoftwareRequest.objects.get(id=pk)
    install_software_request.completion_datetime = datetime.now()
    install_software_request.total_installing_time_in_min = calculate_total_installing_time_for_req(pk)
    install_software_request.manager = request.user
    install_software_request.save()

    serializer = InstallSoftwareRequestSerializer(install_software_request)
    return Response(serializer.data)


# TODO: права
@swagger_auto_schema(method='delete',
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['DELETE'])
def delete_install_software_request(request, pk):
    """
    Удаление заявки на установку ПО
    """
    install_software_request = InstallSoftwareRequest.objects.filter(id=pk,
                                                                     status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    install_software_request.status = InstallSoftwareRequest.RequestStatus.DELETED
    install_software_request.save()
    return Response(status=status.HTTP_200_OK)


# TODO: права
@swagger_auto_schema(method='put',
                     request_body=SoftwareInRequestSerializer,
                     responses={
                         status.HTTP_200_OK: SoftwareInRequestSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['PUT'])
def put_software_in_request(request, request_pk, software_pk):
    """
    Изменение данных о ПО в заявке
    """
    software_in_request = SoftwareInRequest.objects.filter(request_id=request_pk, software_id=software_pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    serializer = SoftwareInRequestSerializer(software_in_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: права
@swagger_auto_schema(method='delete',
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_404_NOT_FOUND: "Not Found",
                     })
@api_view(['DELETE'])
def delete_software_in_request(request, request_pk, software_pk):
    """
    Удаление ПО из заявки
    """
    software_in_request = SoftwareInRequest.objects.filter(request_id=request_pk, software_id=software_pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    software_in_request.delete()
    return Response(status=status.HTTP_200_OK)


# User

@swagger_auto_schema(method='post',
                     request_body=UserSerializer,
                     responses={
                         status.HTTP_201_CREATED: "Created",
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                     })
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Создание пользователя
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post',
                     responses={
                         status.HTTP_200_OK: "OK",
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                     },
                     manual_parameters=[
                         openapi.Parameter('username',
                                           type=openapi.TYPE_STRING,
                                           description='username',
                                           in_=openapi.IN_FORM,
                                           required=True),
                         openapi.Parameter('password',
                                           type=openapi.TYPE_STRING,
                                           description='password',
                                           in_=openapi.IN_FORM,
                                           required=True)
                     ],
                     )
@api_view(['POST'])
@parser_classes((FormParser,))
@permission_classes([AllowAny])
def login_user(request):
    """
    Вход
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        session_id = str(uuid.uuid4())
        session_storage.set(session_id, username)
        response = Response(status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", session_id, samesite="lax")
        return response
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post',
                     responses={
                         status.HTTP_204_NO_CONTENT: "No content",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                     })
@api_view(['POST'])
@permission_classes([IsAuth])
def logout_user(request):
    """
    Выход
    """
    session_id = request.COOKIES["session_id"]
    if session_storage.exists(session_id):
        session_storage.delete(session_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='put',
                     request_body=UserSerializer,
                     responses={
                         status.HTTP_200_OK: UserSerializer(),
                         status.HTTP_400_BAD_REQUEST: "Bad Request",
                         status.HTTP_403_FORBIDDEN: "Forbidden",
                     })
@api_view(['PUT'])
@permission_classes([IsAuth])
@authentication_classes([AuthBySessionID])
def update_user(request):
    """
    Обновление данных пользователя
    """
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
