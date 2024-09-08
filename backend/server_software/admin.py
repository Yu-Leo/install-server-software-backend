from django.contrib import admin

from server_software.models import Software, SoftwareInRequest, Request

admin.site.register(Software)
admin.site.register(Request)
admin.site.register(SoftwareInRequest)
