from django.shortcuts import render

services = [
    {'id': 0, 'title': 'Docker', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/0.png',
     'price': 100,
     'summary': 'Программное обеспечение для автоматизации развёртывания и управления приложениями.'},
    {'id': 1, 'title': 'NodeJS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/1.png',
     'price': 150,
     'summary': 'Программная платформа, основанная на движке V8, которая превращает JavaScript из узкоспециализированного языка в язык общего назначения.'},
    {'id': 2, 'title': 'Python', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/2.png',
     'price': 200,
     'summary': 'Мультипарадигмальный высокоуровневый язык программирования общего назначения с динамической строгой типизацией'},
    {'id': 3, 'title': 'JS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/3.png',
     'price': 300,
     'summary': 'Язык программирования, который в первую очередь применяют в веб-сфере'},
    {'id': 4, 'title': 'git', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/4.png',
     'price': 400,
     'summary': 'Распределённая система управления версиями.'},
]

order = [
    {'id': 0, 'title': 'Docker', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/0.png',
     'price': 100},
    {'id': 1, 'title': 'NodeJS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/1.png',
     'price': 150},
    {'id': 2, 'title': 'Python', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/2.png',
     'price': 200},
]


def get_software_list_page(request):
    search_query = request.GET.get('q', '')

    return render(request, 'services.html',
                  {'data': {
                      'services': [i for i in services if i["title"].startswith(search_query)],
                      'count': len(order)
                  }, })


def get_software_page(request, id):
    for i in services:
        if i['id'] == id:
            return render(request, 'service.html',
                          {'data': i})

    render(request, 'service.html')


def get_order_page(request, id):
    if id != 0:
        return render(request, 'order.html')

    return render(request, 'order.html',
                  {'data': {
                      'services': order,
                  }})
