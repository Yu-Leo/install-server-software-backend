from django.shortcuts import render

software_list = [
    {
        'id': 0,
        'title': 'Docker',
        'logo_file_name': '0.png',
        'price': 100,
        'time': 10,
        'size': '300 Мб',
        'summary': 'Программное обеспечение для автоматизации развёртывания и управления приложениями.',
        'description': 'Docker — программное обеспечение для автоматизации развёртывания и управления приложениями в средах с поддержкой контейнеризации, контейнеризатор приложений. Позволяет «упаковать» приложение со всем своим окружением[англ.] и зависимостями в контейнер, который может быть развёрнут на любой Linux-системе с поддержкой контрольных групп в ядре, а также предоставляет набор команд для управления этими контейнерами. Изначально использовал возможности LXC, с 2015 года начал использовать собственную библиотеку, абстрагирующую виртуализационные возможности ядра Linux — libcontainer. С появлением Open Container Initiative начался переход от монолитной к модульной архитектуре.',
    },

    {
        'id': 1,
        'title': 'NodeJS',
        'logo_file_name': '1.png',
        'price': 150,
        'time': 10,
        'size': '300 Мб',
        'summary': 'Программная платформа, основанная на движке V8, которая превращает JavaScript из узкоспециализированного языка в язык общего назначения.',
        'description': 'Node.js применяется преимущественно на сервере, выполняя роль веб-сервера. Однако есть возможность разрабатывать на Node.js и десктопные оконные приложения, а также программировать микроконтроллеры.',
    },
    {
        'id': 2,
        'title': 'Python',
        'logo_file_name': '2.png',
        'price': 200,
        'time': 20,
        'size': '100 Мб',
        'summary': 'Мультипарадигмальный высокоуровневый язык программирования общего назначения с динамической строгой типизацией',
        'description': 'Мультипарадигмальный высокоуровневый язык программирования общего назначения с динамической строгой типизацией и автоматическим управлением памятью, ориентированный на повышение производительности разработчика, читаемости кода и его качества. Мультипарадигмальный высокоуровневый язык программирования общего назначения с динамической строгой типизацией и автоматическим управлением памятью, ориентированный на повышение производительности разработчика, читаемости кода и его качества, а также на обеспечение переносимости написанных на нём программ. Язык является полностью объектно-ориентированным в том плане, что всё является объектами. Необычной особенностью языка является выделение блоков кода отступами. Синтаксис ядра языка минималистичен, за счёт чего на практике редко возникает необходимость обращаться к документации. Сам же язык известен как интерпретируемый и используется в том числе для написания скриптов',
    },
    {
        'id': 3,
        'title': 'JS',
        'logo_file_name': '3.png',
        'price': 300,
        'time': 43,
        'size': '300 Мб',
        'summary': 'Язык программирования, который в первую очередь применяют в веб-сфере',
        'description': 'Язык программирования, который в первую очередь применяют в веб-сфере. С его помощью сайты делают интерактивными: добавляют всплывающие окна, анимацию, кнопки лайков и формы для отправки информации.',
    },
    {
        'id': 4,
        'title': 'git',
        'logo_file_name': '4.png',
        'price': 400,
        'time': 13,
        'size': '100 Мб',
        'summary': 'Распределённая система управления версиями.',
        'description': 'Распределённая система управления версиями. Проект был создан Линусом Торвальдсом для управления разработкой ядра Linux, первая версия выпущена 7 апреля 2005 года; координатор - Дзюн Хамано. Среди проектов, использующих Git, - ядро Linux, Swift, Android, Drupal, Cairo, GNU Core Utilities, Mesa, Wine, Chromium, Compiz Fusion, FlightGear, jQuery, PHP, NASM, MediaWiki, DokuWiki, Q',
    },
]

user_request = [
    {
        'id': 0,
        'title': 'Docker',
        'logo_file_name': '0.png',
        'price': 100,
    },
    {
        'id': 1,
        'title': 'NodeJS',
        'logo_file_name': '1.png',
        'price': 150,
    },
    {
        'id': 2,
        'title': 'Python',
        'logo_file_name': '2.png',
        'price': 200,
    },
]

MINIO_HOST = '127.0.0.1'
MINIO_PORT = 9000
MINIO_DIR = 'server-soft-logos'


def get_image_file_path(file_name: str) -> str:
    return f'http://{MINIO_HOST}:{MINIO_PORT}/{MINIO_DIR}/{file_name}'


def get_software_list(search_query: str):
    res = []
    for software in software_list:
        if software["title"].lower().startswith(search_query.lower()):
            res.append(software)
            res[-1]['logo_file_path'] = get_image_file_path(software["logo_file_name"])
    return res


def get_request_data():
    res = user_request.copy()
    for i in range(len(res)):
        res[i]['logo_file_path'] = get_image_file_path(res[i]["logo_file_name"])

    s = sum([i['price'] for i in res])
    return {
        'software_list': res,
        'total': s,
    }


def software_list_page(request):
    software_title = request.GET.get('software_title', '')

    return render(request, 'software_list.html',
                  {'data': {
                      'software_list': get_software_list(software_title),
                      'count': len(user_request),
                      'software_title': software_title
                  }, })


def software_page(request, id):
    for software in software_list:
        if software['id'] == id:
            software['logo_file_path'] = get_image_file_path(software["logo_file_name"])
            return render(request, 'software.html',
                          {'data': software})

    render(request, 'software.html')


def request_page(request, id):
    if id != 0:
        return render(request, 'request.html')

    return render(request, 'request.html',
                  {'data': get_request_data()})