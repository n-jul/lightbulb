from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SendTestEmailViewSet, UserCampaignViewSet, MessageViewSet,ScheduleCampaignViewSet,SuperAdminSendCampaignViewSet

router = DefaultRouter()
router.register(r'send_email', SendTestEmailViewSet, basename='send_email')
router.register(r'campaigns', UserCampaignViewSet, basename='usercampaign')
router.register(r'sa_campaigns', SuperAdminSendCampaignViewSet, basename='superadminusercampaign')
# router.register(r'admin/campaigns', AdminUserCampaignViewSet, basename='adminusercampaign')
router.register(r'message', MessageViewSet, basename='Messages')
router.register(r'schedule_campaign',ScheduleCampaignViewSet, basename="schedule_campaign" )
urlpatterns = [
    path('api/', include(router.urls)),
]
