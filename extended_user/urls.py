# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtendedUserViewSet

router = DefaultRouter()
router.register(r'extended_user', ExtendedUserViewSet, basename='extended_user')

urlpatterns = [
    path('api/', include(router.urls)),
]
