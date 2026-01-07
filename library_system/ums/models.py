import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, null=True, unique=True)
    class Meta:
        db_table = "Users"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "ADMIN"),
        ("LIBRARIAN", "LIBRARIAN"),
        ("MEMBER", "MEMBER"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    class Meta:
        db_table = "UserProfiles"

    def __str__(self):
        return f"{self.user.username} - {self.role}"
