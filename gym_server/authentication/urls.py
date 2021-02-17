from rest_framework.routers import DefaultRouter

from .views import RegistrationView, LoginView, RefreshTokenView


router = DefaultRouter()
router.register(r'registration', RegistrationView, basename='user')
router.register(r'login', LoginView, basename='user')
router.register(r'refresh-token', RefreshTokenView, basename='refresh_token')

urlpatterns = router.urls