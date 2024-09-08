from django.db import models
from django.contrib.auth.models import User


class Software(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    price = models.IntegerField()
    installing_time_in_mins = models.IntegerField()
    size_in_bytes = models.IntegerField()
    summary = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    logo_file_path = models.CharField(max_length=255, null=False, default="")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'software'


class Request(models.Model):
    class RequestStatus(models.TextChoices):
        DRAFT = "DRAFT"
        DELETED = "DELETED"
        FORMED = "FORMED"
        COMPLETED = "COMPLETED"
        REJECTED = "REJECTED"

    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
    )

    creation_datetime = models.DateTimeField(auto_now_add=True)
    formation_datetime = models.DateTimeField(blank=True, null=True)
    completion_datetime = models.DateTimeField(blank=True, null=True)
    host = models.CharField(max_length=255)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_requests')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_requests', blank=True, null=True)
    total_installing_time_in_min = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'requests'


class SoftwareInRequest(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    version = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.request_id}-{self.software_id}"

    class Meta:
        db_table = 'software_in_request'
        unique_together = ('request', 'software'),
