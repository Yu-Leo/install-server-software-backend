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
    path('', views.get_software_list, name='software_list'),
    path('add_software_to_cart/', views.add_software_to_cart, name='add_software_to_cart'),
    path('software/<int:id>/', views.software_page, name='software'),
    path('install_software_request/<int:id>/', views.get_software_request, name='install_software_request'),
    path('remove_software_request/<int:id>/', views.remove_software_request, name='remove_software_request'),
]
