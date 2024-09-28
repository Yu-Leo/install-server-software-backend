from .models import Software, InstallSoftwareRequest, SoftwareInRequest

from rest_framework import serializers


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = ["pk", "title", "price", "installing_time_in_mins", "size_in_bytes", "summary", "description", "is_active", "logo_file_path" ]

class InstallSoftwareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client", "manager", "total_installing_time_in_min"]

class SoftwareInRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareInRequest
        fields = ["pk", "request", "software", "version"]
