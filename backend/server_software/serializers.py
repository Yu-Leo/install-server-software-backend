from .models import Software, InstallSoftwareRequest, SoftwareInRequest

from rest_framework import serializers


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = ["pk", "title", "price", "installing_time_in_mins", "size_in_bytes", "summary", "description",
                  "is_active", "logo_file_path"]


class InstallSoftwareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client", "manager",
                  "total_installing_time_in_min", "status"]


class PutInstallSoftwareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client", "manager",
                  "total_installing_time_in_min", "status"]
        read_only_fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "client", "manager",
                            "total_installing_time_in_min", "status"]


class ResolveInstallSoftwareRequestSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data.get('status', '') not in (
                InstallSoftwareRequest.RequestStatus.COMPLETED, InstallSoftwareRequest.RequestStatus.REJECTED,):
            raise serializers.ValidationError("invalid status")
        return data

    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client", "manager",
                  "total_installing_time_in_min", "status"]
        read_only_fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client",
                            "manager",
                            "total_installing_time_in_min"]


class SoftwareInRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareInRequest
        fields = ["pk", "request", "software", "version"]


class SoftwareForRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = ["pk", "title", "price", "summary", "logo_file_path"]


class RelatedSerializer(serializers.ModelSerializer):
    software = SoftwareForRequestSerializer()

    class Meta:
        model = SoftwareInRequest
        fields = ["software", "version"]


class FullInstallSoftwareRequestSerializer(serializers.ModelSerializer):
    software_list = RelatedSerializer(source='softwareinrequest_set', many=True)

    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "client", "manager",
                  "total_installing_time_in_min", "status", "software_list"]
