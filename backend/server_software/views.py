from datetime import datetime

from django.shortcuts import render, redirect
from django.db import connection
from django.db.models import Q

from server_software.models import Software, InstallSoftwareRequest, SoftwareInRequest

USER_ID = 1


def get_request_data(request_id: int):
    req = InstallSoftwareRequest.objects.filter(~Q(status=InstallSoftwareRequest.RequestStatus.DELETED),
                                                id=request_id).first()
    if req is None:
        return {
            'id': request_id,
            'software_list': [],
            'total': 0,
            'req_id': request_id,
            'user_host': '',
        }

    items = SoftwareInRequest.objects.filter(request_id=request_id).select_related('software')
    s = sum([i.software.price for i in items])
    return {
        'id': request_id,
        'software_list': items,
        'total': s,
        'req_id': request_id,
        'user_host': req.host,
    }


def get_items_in_request(request_id: int) -> int:
    """
    Получение колическа элементов в заявке по её id
    """
    return SoftwareInRequest.objects.filter(request_id=request_id).select_related('software').count()


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


def get_software_list(request):
    software_title = request.GET.get('software_title', '')
    req = InstallSoftwareRequest.objects.filter(client_id=USER_ID,
                                                status=InstallSoftwareRequest.RequestStatus.DRAFT).first()
    software_list = Software.objects.filter(title__istartswith=software_title, is_active=True)
    return render(request, 'software_list.html',
                  {'data':
                      {
                          'software_list': software_list,
                          'items_in_cart': (get_items_in_request(req.id) if req is not None else 0),
                          'software_title': software_title,
                          'request_id': (req.id if req is not None else 0),
                      },
                  })


def add_software_to_cart(request):
    if request.method != "POST":
        return redirect('software_list')
    data = request.POST
    software_id = data.get("add_to_cart")
    if software_id is not None:
        request_id = get_or_create_user_cart(USER_ID)
        add_item_to_request(request_id, software_id)
    return redirect('software_list')


def software_page(request, id):
    data = Software.objects.filter(id=id).first()
    if data is None:
        return render(request, 'software.html')

    return render(request, 'software.html',
                  {'data': {
                      'software': data,
                  }})


def delete_request(request_id: int):
    """
    Удаление заявки по id
    """
    raw_sql = "UPDATE install_software_requests SET status='DELETED' WHERE id=%s "
    with connection.cursor() as cursor:
        cursor.execute(raw_sql, (request_id,))


def remove_software_request(request, id: int):
    if request.method != "POST":
        return redirect('install_software_request')

    data = request.POST
    action = data.get("request_action")
    if action == "delete_request":
        delete_request(id)
        return redirect('software_list')
    return redirect('install_software_request')


def get_software_request(request, id: int):
    return render(request, 'request.html',
                  {'data': get_request_data(id)})
