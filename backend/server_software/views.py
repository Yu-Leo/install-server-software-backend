from rest_framework.decorators import api_view
from rest_framework.response import *
from rest_framework import status
from django.db.models import Q
from dateutil.parser import parse

from .models import Software, InstallSoftwareRequest, SoftwareInRequest
from server_software.serializers import InstallSoftwareRequestSerializer, SoftwareInRequestSerializer, \
    SoftwareSerializer

USER_ID = 1


# Software

@api_view(['GET'])
def GetSoftwareList(request):
    """
    Получение списка ПО
    """
    software_title = request.query_params.get("software_title", "")
    req = InstallSoftwareRequest.objects.filter(client_id=USER_ID,
                                                status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    software_list = Software.objects.filter(title__istartswith=software_title, is_active=True)

    serializer = SoftwareSerializer(software_list, many=True)
    return Response(
        {
            "software": serializer.data,
            "install_software_request_id": req.id if req else None
        },
        status=status.HTTP_200_OK)


@api_view(['POST'])
def PostSoftware(request):
    """
    Добавление ПО
    """
    serializer = SoftwareSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_software = serializer.save()
    serializer = SoftwareSerializer(new_software)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def GetSoftware(request, pk):
    """
    Получение ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    serialized_software = SoftwareSerializer(software)
    return Response(serialized_software.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def DeleteSoftware(request, pk):
    """
    Удаление ПО
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    software.is_active = False
    software.save()

    # TODO: удаление изображения
    return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
def PutSoftware(request, pk):
    """
    Изменение ПО
    """
    software = Software.objects.filter(id=pk).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)

    serializer = SoftwareSerializer(software, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        software = Software.objects.get(id=pk)
        serializer = SoftwareSerializer(software)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def PostSoftwareToRequest(request, pk):
    """
    Добавление ПО в заявку на установку
    """
    software = Software.objects.filter(id=pk, is_active=True).first()
    if software is None:
        return Response("Software not found", status=status.HTTP_404_NOT_FOUND)
    request_id = get_or_create_user_cart(USER_ID)
    add_item_to_request(request_id, pk)
    return Response(status=status.HTTP_200_OK)


def get_or_create_user_cart(user_id: int) -> int:
    """
    Если у пользователя есть заявка в статусе DRAFT (корзина), возвращает её Id.
    Если нет - создает и возвращает id созданной заявки
    """
    old_req = InstallSoftwareRequest.objects.filter(client_id=USER_ID,
                                                    status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if old_req is not None:
        return old_req.id

    new_req = InstallSoftwareRequest(client_id=USER_ID, status=InstallSoftwareRequest.RequestStatus.DRAFT)
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
def GetInstallSoftwareRequests(request):
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
def GetInstallSoftwareRequest(request, pk):
    """
    Получение заявки на установку ПО
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['PUT'])
def PutInstallSoftwareRequest(request, pk):
    """
    Изменение заявки на установку ПО
    """
    install_software_request = InstallSoftwareRequest.objects.filter(id=pk,
                                                                     status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if install_software_request is None:
        return Response("InstallSoftwareRequest not found", status=status.HTTP_404_NOT_FOUND)

    serializer = InstallSoftwareRequestSerializer(install_software_request,
                                                  data=request.data,
                                                  partial=True)
    if serializer.is_valid():
        serializer.save()
        install_software_request = InstallSoftwareRequest.objects.get(id=pk)
        serializer = InstallSoftwareRequestSerializer(install_software_request)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def FormInstallSoftwareRequest(request, pk):
    """
    Формирование заявки на установку ПО
    """

    return Response("Not implemented", status=501)  # TODO


@api_view(['PUT'])
def ResolveInstallSoftwareRequest(request, pk):
    """
    Закрытие заявки на установку ПО модератором
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['DELETE'])
def DeleteInstallSoftwareRequest(request, pk):
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
def PutSoftwareInRequest(request, pk):
    """
    Изменение данных о ПО в заявке
    """
    software_in_request = SoftwareInRequest.objects.filter(id=pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    serializer = SoftwareInRequestSerializer(software_in_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        software_in_request = SoftwareInRequest.objects.get(id=pk)
        serializer = SoftwareInRequestSerializer(software_in_request)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def DeleteSoftwareInRequest(request, pk):
    """
    Удаление ПО из заявки
    """
    software_in_request = SoftwareInRequest.objects.filter(id=pk).first()
    if software_in_request is None:
        return Response("SoftwareInRequest not found", status=status.HTTP_404_NOT_FOUND)
    software_in_request.delete()
    return Response(status=status.HTTP_200_OK)
