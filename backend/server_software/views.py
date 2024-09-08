from datetime import datetime

from django.shortcuts import render, redirect
from django.db import connection

from server_software.models import Software, Request, SoftwareInRequest

USER_ID = 1


def get_request_data(request_id: int):
    req = Request.objects.filter(id=request_id).first()
    items = SoftwareInRequest.objects.filter(request_id=request_id).select_related('software')
    s = sum([i.software.price for i in items])
    return {
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
    old_req = Request.objects.filter(client_id=USER_ID, status=Request.RequestStatus.DRAFT).first()
    if old_req is not None:
        return old_req.id

    new_req = Request(client_id=USER_ID, status=Request.RequestStatus.DRAFT)
    new_req.save()
    return new_req.id


def add_item_to_request(request_id: int, software_id: int):
    """
    Добавление услуги в заявку
    """
    sir = SoftwareInRequest(request_id=request_id, software_id=software_id)
    sir.save()


def software_list_page(request):
    if request.method == "POST":
        data = request.POST
        software_id = data.get("add_to_cart")
        if software_id is not None:
            request_id = get_or_create_user_cart(USER_ID)
            add_item_to_request(request_id, software_id)

    software_title = request.GET.get('software_title', '')
    req = Request.objects.filter(client_id=USER_ID, status=Request.RequestStatus.DRAFT).first()
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
    raw_sql = "UPDATE requests SET status='DELETED' WHERE id=%s "
    with connection.cursor() as cursor:
        cursor.execute(raw_sql, (request_id,))


def form_request(request_id: int, data):
    """
    Формирование заявки
    """
    user_host = data.get('user_host')
    items = SoftwareInRequest.objects.filter(request_id=request_id)
    for i in items:
        SoftwareInRequest.objects.filter(request_id=request_id, software_id=i.software_id).update(
            version=data.get(f'{request_id}-{i.software_id}'))
    Request.objects.filter(id=request_id).update(
        status=Request.RequestStatus.FORMED,
        formation_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        host=user_host)


def request_page(request, id: int):
    if request.method == "POST":
        data = request.POST
        action = data.get("request_action")
        if action == "delete_request":
            delete_request(id)
            return redirect('software_list')
        elif action == "form_request":
            form_request(id, data)
            return redirect('software_list')

    return render(request, 'request.html',
                  {'data': get_request_data(id)})
