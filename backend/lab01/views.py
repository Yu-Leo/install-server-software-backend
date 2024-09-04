from django.shortcuts import render


def get_services(request):
    if request.method == "POST":
        input_text = request.POST['text']
    else:
        input_text = ""
    print(input_text)
    services = [
        {'id': 1, 'title': 'Docker', 'logo_file_name': 'logo-docker.png', 'price': 100},
        {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'logo-node-js.png', 'price': 150},
        {'id': 3, 'title': 'Python', 'logo_file_name': 'logo-python.png', 'price': 200},
        {'id': 4, 'title': 'JS', 'logo_file_name': 'logo-javascript.png', 'price': 300},
        {'id': 5, 'title': 'git', 'logo_file_name': 'logo-git.png', 'price': 400},
    ]

    return render(request, 'services.html',
                  {'data': {
                      'services': [i for i in services if i["title"].startswith(input_text)]
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


def get_order(request, id):
    if id != 0:
        return render(request, 'order.html')

    return render(request, 'order.html',
                  {'data': {
                      'services': [
                          {'id': 1, 'title': 'Docker', 'logo_file_name': 'logo-docker.png', 'price': 100},
                          {'id': 2, 'title': 'NodeJS', 'logo_file_name': 'logo-node-js.png', 'price': 150},
                          {'id': 3, 'title': 'Python', 'logo_file_name': 'logo-python.png', 'price': 200},
                      ]
                  }})
