from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtendedUserViewSet, LoginView, PracticeViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'signup', ExtendedUserViewSet, basename='Signup')
router.register(r'practice',PracticeViewSet, basename='practice')
# Define URL patterns
urlpatterns = [
    path('api/', include(router.urls)),  # Include signup viewset via router
    path('api/login/', LoginView.as_view(), name="Login")  # Manually add login URL
]
