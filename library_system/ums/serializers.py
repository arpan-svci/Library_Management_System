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
        fields = ("username", "first_name", "last_name", "email", "password", "role")  # Fields to include
        extra_kwargs = {
            "password": {"write_only": True},  # Password should never be read back
            "email": {"required": False} 
        }

    def create(self, validated_data):
        role = validated_data.pop("role")

        user = User.objects.create_user(
            username=validated_data.get("username",None),
            email=validated_data.get("email",None),
            first_name = validated_data.get("first_name",None),
            last_name = validated_data.get("last_name",None),
            password=validated_data.get("password",None),
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        return user

class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "role",
        ]

    def get_role(self, obj):
        return getattr(obj.userprofile, "role", None)
    
class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
        )
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }
    def validate_email(self, value):
        if value:  # only validate if email is provided
            if User.objects.exclude(id=self.instance.id).filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value

    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)

        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update role in UserProfile if provided
        if role:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.role = role
            profile.save()

        return instance