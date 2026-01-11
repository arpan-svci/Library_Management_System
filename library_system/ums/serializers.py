from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)

    class Meta:
        model = User  # The model this serializer is for
        fields = ("username", "email", "password", "role")  # Fields to include
        extra_kwargs = {
            "password": {"write_only": True},  # Password should never be read back
            "email": {"required": False} 
        }

    def create(self, validated_data):
        role = validated_data.pop("role")

        user = User.objects.create_user(
            username=validated_data.get("username",None),
            email=validated_data.get("email",None),
            password=validated_data.get("password",None),
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        return user

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        ]