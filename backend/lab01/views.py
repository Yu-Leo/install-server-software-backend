from django.shortcuts import render

services = [
    {'id': 1, 'title': 'Docker', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-docker.png',
     'price': 100},
    {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-node-js.png',
     'price': 150},
    {'id': 3, 'title': 'Python', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-python.png',
     'price': 200},
    {'id': 4, 'title': 'JS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-javascript.png',
     'price': 300},
    {'id': 5, 'title': 'git', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-git.png', 'price': 400},
]

order = [
    {'id': 1, 'title': 'Docker', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-docker.png',
     'price': 100},
    {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-node-js.png',
     'price': 150},
    {'id': 3, 'title': 'Python', 'logo_file_name': 'http://172.19.0.3:9000/server-soft-logos/logo-python.png',
     'price': 200},
]


def get_services(request):
    if request.method == "POST":
        input_text = request.POST['text']
    else:
        input_text = ""
    print(input_text)

    return render(request, 'services.html',
                  {'data': {
                      'services': [i for i in services if i["title"].startswith(input_text)],
                      'count': len(order)
                  },})


def get_service(request, id):
    for i in services:
        if i['id'] == id:
            return render(request, 'service.html',
                          {'data': i})
    render(request, 'service.html')


def get_order(request, id):
    if id != 0:
        return render(request, 'order.html')

    return render(request, 'order.html',
                  {'data': {
                      'services': order,
                  }})
