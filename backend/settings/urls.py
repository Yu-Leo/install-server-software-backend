"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from server_software import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Software

    path('software', views.get_software_list, name='software_list'),
    path('software/post', views.post_software, name='software_post'),
    path('software/<int:pk>', views.get_software, name='software'),
    path('software/<int:pk>/delete', views.delete_software, name='software_delete'),
    path('software/<int:pk>/put', views.put_software, name='software_put'),
    path('software/<int:pk>/add', views.post_software_to_request, name='software_add'),
    path('software/<int:pk>/add_image', views.post_software_image, name='software_add_image'),

    # InstallSoftwareRequest

    path('install_software_requests', views.get_install_software_requests, name='install_software_requests'),
    path('install_software_requests/<int:pk>', views.get_install_software_request, name='install_software_request'),
    path('install_software_requests/<int:pk>/put', views.put_install_software_request,
         name='install_software_request_put'),
    path('install_software_requests/<int:pk>/form', views.form_install_software_request,
         name='install_software_request_form'),
    path('install_software_requests/<int:pk>/resolve', views.resolve_install_software_request,
         name='install_software_request_resolve'),
    path('install_software_requests/<int:pk>/delete', views.delete_install_software_request,
         name='install_software_request_delete'),

    # SoftwareInRequest

    path('software_in_request/<int:pk>/put', views.put_software_in_request, name='software_in_request_put'),
    path('software_in_request/<int:pk>/delete', views.delete_software_in_request, name='software_in_request_delete'),

    # User

    path('users/create', views.create_user, name='users_create'),
    path('users/login', views.login_user, name='users_login'),
    path('users/logout', views.logout_user, name='users_logout'),
    path('users/update', views.update_user, name='users_update'),
]
