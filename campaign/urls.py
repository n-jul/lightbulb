from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SendTestEmailViewSet, UserCampaignViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'send_email', SendTestEmailViewSet, basename='send_email')
router.register(r'campaigns', UserCampaignViewSet, basename='usercampaign')
router.register(r'message', MessageViewSet, basename='Messages')

urlpatterns = [
    path('api/', include(router.urls)),
]
