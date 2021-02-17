from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .serializers import (
    StaffProfileSerializer, ClientProfileSerializer, PositionModelSerializer,
    SubscriptionModelSerializer, ServiceModelSerializer
)
from .mixins import CheckValidParamMixin
from .models import StaffProfileModel, ClientProfileModel, PositionModel, SubscriptionModel, ServiceModel
from .filters import PositionFilter, SubscriptionFilter, ServiceFilter, ProfileFilter
from .errors import RoleURLParamError, ExpireError
from .permissions import ClientOnly, StaffOnly


class UserViewSet(CheckValidParamMixin,
                  viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filterset_class = ProfileFilter
    role = None
    client_role = 1
    staff_role = 2

    def get_role(self, request):
        try:
            obj = int(request.GET.get('role', None))
        except TypeError:
            obj = None
        return obj

    def check_role_permissions(self, request, role, instance=None):
        if request.user.role != role \
                and not request.user.is_superuser \
                or instance\
                and request.user.id  != instance.user.id\
                and not request.user.is_superuser:
            self.permission_denied(
                request,
                message="You do not have permission to perform this action."
            )

    def get_object(self):
        queryset = None
        if self.role == self.client_role:
            queryset = self.filter_queryset(ClientProfileModel.objects.all())
        elif self.role == self.staff_role:
            queryset = self.filter_queryset(StaffProfileModel.objects.all())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer(self, *args, **kwargs):
        if self.role == self.client_role:
            serializer_class = ClientProfileSerializer
        elif self.role == self.staff_role:
            serializer_class = StaffProfileSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        if self.role == self.client_role:
            queryset = self.filter_queryset(ClientProfileModel.objects.all())
        elif self.role == self.staff_role:
            queryset = self.filter_queryset(StaffProfileModel.objects.all())
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        self.role = self.get_role(request)
        self.check_role_permissions(request, self.staff_role)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        self.role = self.get_role(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        self.check_role_permissions(request, self.role, instance)

        if self.role == self.client_role:
            if instance.is_expired:
                headers = {"error": ExpireError.msg}
                return Response(serializer.data, headers=headers)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        self.role = self.get_role(request)
        self.check_role_permissions(request, self.role)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        self.role = self.get_role(request)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        self.check_role_permissions(request, self.role, instance)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.role = self.get_role(request)
        instance = self.get_object()

        self.check_role_permissions(request, self.role, instance)

        user_id = self.perform_destroy(instance)
        return Response({"delete_message": f"User id:{user_id} is deactivated."},
                        status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.user.is_active = False
        instance.user.save()
        try:
            instance.subscription.delete()
        except AttributeError:
            pass
        instance.delete()
        return instance.user.id


class SubscriptionListView(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = ((StaffOnly|IsAdminUser),)
    filterset_class = SubscriptionFilter
    serializer_class = SubscriptionModelSerializer
    queryset = SubscriptionModel.objects.all()


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceModelSerializer
    filterset_class = ServiceFilter
    queryset = ServiceModel.objects.all()
    permission_classes_by_action = {'list': [ClientOnly|StaffOnly|IsAdminUser],
                                    'retrieve': [ClientOnly|StaffOnly|IsAdminUser],
                                    'default': [StaffOnly|IsAdminUser]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['default']]


class PositionViewSet(viewsets.ModelViewSet):
    permission_classes = ((StaffOnly|IsAdminUser),)
    filterset_class = PositionFilter
    serializer_class = PositionModelSerializer
    queryset = PositionModel.objects.all()
