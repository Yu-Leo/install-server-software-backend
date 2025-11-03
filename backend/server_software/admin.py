from django.contrib import admin

from server_software.models import Software, SoftwareInRequest, InstallSoftwareRequest

admin.site.register(Software)
admin.site.register(InstallSoftwareRequest)
admin.site.register(SoftwareInRequest)
