from django.shortcuts import render


def get_services(request):
    return render(request, 'services.html',
                  {'data': {
                      'services': [
                          {'id': 1, 'title': 'Docker', 'logo_file_name': 'logo-docker.png', 'price': 100},
                          {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'logo-node-js.png', 'price': 150},
                          {'id': 3, 'title': 'Python', 'logo_file_name': 'logo-python.png', 'price': 200},
                          {'id': 4, 'title': 'JS', 'logo_file_name': 'logo-javascript.png', 'price': 300},
                          {'id': 5, 'title': 'git', 'logo_file_name': 'logo-git.png', 'price': 400},
                      ]
                  }})


def get_service(request, id):
    services = {
        1: {'title': 'Docker', 'logo_file_name': 'logo-docker.png', 'price': 100, 'size': '500Mb'},
        2: {'title': 'NodeJS', 'logo_file_name': 'logo-node-js.png', 'price': 150, 'size': '100Mb'},
        3: {'title': 'Python', 'logo_file_name': 'logo-python.png', 'price': 200, 'size': '1Gb'},
        4: {'title': 'JS', 'logo_file_name': 'logo-javascript.png', 'price': 300, 'size': '800Mb'},
        5: {'title': 'git', 'logo_file_name': 'logo-git.png', 'price': 400, 'size': '30Mb'},
    }

    return render(request, 'service.html',
                  {'data': services[id]})


def get_order(request):
    return render(request, 'order.html',
                  {'data': {
                      'services': [
                          {'id': 1, 'title': 'Docker', 'logo_file_name': 'logo-docker.png', 'price': 100},
                          {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'logo-node-js.png', 'price': 150},
                          {'id': 3, 'title': 'Python', 'logo_file_name': 'logo-python.png', 'price': 200},
                      ]
                  }})


def send_text(request):
    input_text = request.POST['text']
    print(input_text)
    return render(request, 'services.html')