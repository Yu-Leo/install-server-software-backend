from rest_framework.decorators import api_view
from rest_framework.response import *
from rest_framework import status

from .models import Software
from server_software.serializers import SoftwareSerializer


# Software

@api_view(['GET'])
def GetSoftwareList(request):
    """
    Получение списка ПО
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['POST'])
def PostSoftware(request):
    """
    Добавление программы
    """
    return Response("Not implemented", status=501)  # TODO


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
    return Response("Not implemented", status=501)  # TODO


@api_view(['PUT'])
def PutSoftware(request, pk):
    """
    Изменение ПО
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['POST'])
def PostSoftwareToRequest(request, pk):
    """
    Добавление ПО в заявку на установку
    """
    return Response("Not implemented", status=501)  # TODO


# InstallSoftwareRequest

@api_view(['GET'])
def GetInstallSoftwareRequests(request):
    """
    Получение списка заявок на установку ПО
    """
    return Response("Not implemented", status=501)  # TODO


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
    return Response("Not implemented", status=501)  # TODO


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
    return Response("Not implemented", status=501)  # TODO


@api_view(['PUT'])
def PutSoftwareInRequest(request, pk):
    """
    Изменение данных о ПО в заявке
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['DELETE'])
def DeleteSoftwareInRequest(request, pk):
    """
    Удаление ПО из заявки
    """
    return Response("Not implemented", status=501)  # TODO
