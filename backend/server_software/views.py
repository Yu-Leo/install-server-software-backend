import os

from datetime import datetime
from dateutil.parser import parse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from settings import settings
from .minio import MinioStorage
from server_software.serializers import *

SINGLETON_USER = User(id=1, username="admin")
SINGLETON_MANAGER = User(id=2, username="manager")


# Software

@api_view(['GET'])
def get_software_list(request):
    """
    Получение списка ПО
    """
    software_title = request.query_params.get("software_title", "")
    software_list = Software.objects.filter(title__istartswith=software_title, is_active=True)

    req = InstallSoftwareRequest.objects.filter(client_id=SINGLETON_USER.id,
                                                status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    items_in_cart = 0
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


@api_view(['POST'])
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


@api_view(['POST'])
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


@api_view(['GET'])
def get_software(request, pk):
    """
    Получение ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    serialized_software = SoftwareSerializer(software)
    return Response(serialized_software.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
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


@api_view(['PUT'])
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


@api_view(['POST'])
def post_software_to_request(request, pk):
    """
    Добавление ПО в заявку на установку
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    request_id = get_or_create_user_cart(SINGLETON_USER.id)
    add_item_to_request(request_id, pk)
    return Response(status=status.HTTP_200_OK)


def get_or_create_user_cart(user_id: int) -> int:
    """
    Если у пользователя есть заявка в статусе DRAFT (корзина), возвращает её Id.
    Если нет - создает и возвращает id созданной заявки
    """
    old_req = InstallSoftwareRequest.objects.filter(client_id=SINGLETON_USER.id,
                                                    status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if old_req is not None:
        return old_req.id

    new_req = InstallSoftwareRequest(client_id=SINGLETON_USER.id,
                                     status=InstallSoftwareRequest.RequestStatus.DRAFT)
    new_req.save()
    return new_req.id


def add_item_to_request(request_id: int, software_id: int):
    """
    Добавление услуги в заявку
    """
    sir = SoftwareInRequest(request_id=request_id, software_id=software_id)
    sir.save()


# InstallSoftwareRequest

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

    install_software_requests = InstallSoftwareRequest.objects.filter(filters)
    serializer = InstallSoftwareRequestSerializer(install_software_requests, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


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


def is_valid_versions(request_id):
    """
    Проверка: у всего ПО из заявки должна быть указана версия
    """
    software_in_request = SoftwareInRequest.objects.filter(request_id=request_id)
    for software in software_in_request:
        if software.version is None or software.version == "":
            return False
    return True


@api_view(['PUT'])
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
    install_software_request.SINGLETON_MANAGER = SINGLETON_MANAGER
    install_software_request.save()

    serializer = InstallSoftwareRequestSerializer(install_software_request)
    return Response(serializer.data)


def calculate_total_installing_time_for_req(pk):
    """
    Расчет суммарного времени на установку всего ПО из заявки
    """
    soft = SoftwareInRequest.objects.select_related("software").filter(request=pk)
    return sum([s.software.installing_time_in_mins for s in soft])


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


@api_view(['PUT'])
def put_software_in_request(request, pk):
    """
    Изменение данных о ПО в заявке
    """
    software_in_request = SoftwareInRequest.objects.filter(id=pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    serializer = SoftwareInRequestSerializer(software_in_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_software_in_request(request, pk):
    """
    Удаление ПО из заявки
    """
    software_in_request = SoftwareInRequest.objects.filter(id=pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    software_in_request.delete()
    return Response(status=status.HTTP_200_OK)


# User

@api_view(['POST'])
def create_user(request):
    """
    Создание пользователя
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    """
    Вход
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Выход
    """
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
    """
    Обновление данных пользователя
    """
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
