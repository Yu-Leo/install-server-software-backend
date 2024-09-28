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
from django.urls import path, include

from server_software import views

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),

    # Software

    path('software', views.GetSoftwareList, name='software_list'),
    path('software/post', views.PostSoftware, name='software_post'),
    path('software/<int:pk>', views.GetSoftware, name='software'),
    path('software/<int:pk>/delete', views.DeleteSoftware, name='software_delete'),
    path('software/<int:pk>/put', views.PutSoftware, name='software_put'),
    path('software/<int:pk>/add', views.PostSoftwareToRequest, name='software_add'),

    # InstallSoftwareRequest

    path('install_software_requests', views.GetInstallSoftwareRequests, name='install_software_requests'),
    path('install_software_requests/<int:pk>', views.GetInstallSoftwareRequest, name='install_software_request'),
    path('install_software_requests/<int:pk>/put', views.PutInstallSoftwareRequest,
         name='install_software_request_put'),
    path('install_software_requests/<int:pk>/form', views.FormInstallSoftwareRequest,
         name='install_software_request_form'),
    path('install_software_requests/<int:pk>/resolve', views.ResolveInstallSoftwareRequest,
         name='install_software_request_resolve'),
    path('install_software_requests/<int:pk>/delete', views.DeleteInstallSoftwareRequest,
         name='install_software_request_delete'),

    # SoftwareInRequest

    path('software_in_request/<int:pk>/put', views.PutSoftwareInRequest, name='software_in_request_put'),
    path('software_in_request/<int:pk>/delete', views.DeleteSoftwareInRequest, name='software_in_request_delete'),

]
