from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SendTestEmailViewSet

router = DefaultRouter()
router.register(r'send_email', SendTestEmailViewSet, basename='send_email')

urlpatterns = [
    path('api/', include(router.urls)),
]
