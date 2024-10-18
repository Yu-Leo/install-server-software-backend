from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Software, InstallSoftwareRequest, SoftwareInRequest


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = ["pk", "title", "price", "installing_time_in_mins", "size_in_bytes", "summary", "description",
                  "is_active", "logo_file_path"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class InstallSoftwareRequestSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    def get_client(self, obj):
        return obj.client.username

    class Meta:
        model = InstallSoftwareRequest
        fields = ["pk", "creation_datetime", "formation_datetime", "completion_datetime", "host", "manager",
                  "total_installing_time_in_min", "status", "client"]


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
        fields = ["request", "software", "version"]


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
