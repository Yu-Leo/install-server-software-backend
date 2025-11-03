from server_software.serializers import *


def get_or_create_user_cart(user_id: int) -> int:
    """
    Если у пользователя есть заявка в статусе DRAFT (корзина), возвращает её Id.
    Если нет - создает и возвращает id созданной заявки
    """
    old_req = InstallSoftwareRequest.objects.filter(client_id=user_id,
                                                    status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    if old_req is not None:
        return old_req.id

    new_req = InstallSoftwareRequest(client_id=user_id,
                                     status=InstallSoftwareRequest.RequestStatus.DRAFT)
    new_req.save()
    return new_req.id


def is_valid_versions(request_id):
    """
    Проверка: у всего ПО из заявки должна быть указана версия
    """
    software_in_request = SoftwareInRequest.objects.filter(request_id=request_id)
    for software in software_in_request:
        if software.version is None or software.version == "":
            return False
    return True


def calculate_total_installing_time_for_req(pk):
    """
    Расчет суммарного времени на установку всего ПО из заявки
    """
    soft = SoftwareInRequest.objects.select_related("software").filter(request=pk)
    return sum([s.software.installing_time_in_mins for s in soft])


def add_item_to_request(request_id: int, software_id: int):
    """
    Добавление услуги в заявку
    """
    sir = SoftwareInRequest(request_id=request_id, software_id=software_id)
    sir.save()
