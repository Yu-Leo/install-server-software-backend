from rest_framework.decorators import api_view
from rest_framework.response import *


# Software

@api_view(['GET'])
def GetSoftwareList(request):
    """
    Получение списка программ
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
    Получение программы
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['DELETE'])
def DeleteSoftware(request, pk):
    """
    Удаление программы
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['PUT'])
def PutSoftware(request, pk):
    """
    Изменение программы
    """
    return Response("Not implemented", status=501)  # TODO


@api_view(['POST'])
def PostSoftwareToRequest(request, pk):
    """
    Добавление программы в заявку на установку
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
