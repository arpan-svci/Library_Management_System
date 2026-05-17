from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterAPI, DeleteUserAPI, ListUsersAPI, EditUserAPI

urlpatterns = [
    path("register/", RegisterAPI.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("delete/<uuid:user_id>/", DeleteUserAPI.as_view()),
    path("users/", ListUsersAPI.as_view()),
    path("edit/<uuid:user_id>/", EditUserAPI.as_view()),
]