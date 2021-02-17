from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PositionViewSet, SubscriptionListView, ServiceViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'subscriptions', SubscriptionListView, basename='subscription')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = router.urls