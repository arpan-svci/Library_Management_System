from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

from .serializers import UserCreateSerializer, UserListSerializer, UserUpdateSerializer, UserDetailSerializer
from .permissions import IsSuperUser
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiTypes

from django.contrib.auth import get_user_model

User = get_user_model()

import logging

logger = logging.getLogger(__name__)


class RegisterAPI(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    @extend_schema(request=UserCreateSerializer, responses={201: OpenApiTypes.OBJECT})
    def post(self, request):
        logger.info("RegisterAPI POST called by user_id=%s", getattr(request.user, 'id', None))
        logger.debug("RegisterAPI request.data=%s", request.data)
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info("User created successfully id=%s by user_id=%s", user.id, getattr(request.user, 'id', None))
            return Response(
                {"message": "User created successfully", "user_id": user.id},
                status=status.HTTP_201_CREATED
            )
        logger.warning("RegisterAPI serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserAPI(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def delete(self, request, user_id):
        logger.info("DeleteUserAPI DELETE called by user_id=%s for target_user_id=%s", getattr(request.user, 'id', None), user_id)

        # Prevent self-delete
        if request.user.id == user_id:
            logger.warning("Attempted self-delete by user_id=%s", request.user.id)
            return Response(
                {"error": "You cannot delete yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("DeleteUserAPI: user not found id=%s", user_id)
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # prevent deleting superuser
        if user.is_superuser:
            logger.warning("Attempted to delete superuser id=%s by user_id=%s", user.id, getattr(request.user, 'id', None))
            return Response(
                {"error": "Cannot delete a superuser"},
                status=status.HTTP_403_FORBIDDEN
            )

        user.delete()
        logger.info("User deleted successfully id=%s by user_id=%s", user.id, getattr(request.user, 'id', None))
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )
    
class ListUsersAPI(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    # Hint for drf-spectacular and other tools that expect a serializer
    serializer_class = UserListSerializer

    @extend_schema(responses=UserListSerializer(many=True))
    def get(self, request):
        users_qs = User.objects.filter(is_superuser=False).order_by("-date_joined")

        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)

        paginator = Paginator(users_qs, page_size)
        page_obj = paginator.get_page(page)

        serializer = UserListSerializer(page_obj, many=True)

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "results": serializer.data
        })
    
class EditUserAPI(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    @extend_schema(request=UserUpdateSerializer, responses={200: OpenApiTypes.OBJECT})
    def put(self, request, user_id):
        logger.info(
            "EditUserAPI called by user_id=%s for target_user_id=%s",
            getattr(request.user, "id", None),
            user_id,
        )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("User not found id=%s", user_id)
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent editing superuser (optional safety)
        if user.is_superuser:
            return Response(
                {"error": "Cannot edit a superuser"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            logger.info("User updated successfully id=%s", user.id)
            return Response(
                {"message": "User updated successfully"},
                status=status.HTTP_200_OK,
            )

        logger.warning("EditUserAPI errors: %s", serializer.errors)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetUserAPI(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get(self, request, user_id):
        logger.info(
            "GetUserAPI GET called by user_id=%s for target_user_id=%s",
            getattr(request.user, "id", None),
            user_id,
        )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("GetUserAPI: user not found id=%s", user_id)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Do not expose superuser details via this endpoint
        if user.is_superuser:
            logger.warning("GetUserAPI: attempted to access superuser id=%s by user_id=%s", user.id, getattr(request.user, "id", None))
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)