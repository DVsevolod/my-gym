import django_filters

from django.db.models import Q

from .models import (PositionModel, SubscriptionModel, ServiceModel)
from .utils import get_expire_date


class ProfileFilter(django_filters.FilterSet):
    # Filter both profiles by created date
    created_gt = django_filters.DateFilter('user__created_at', lookup_expr='gt')
    created_lt = django_filters.DateFilter('user__created_at', lookup_expr='lt')
    # Filters for ClientProfile  /users/?role=1&...
    service_name = django_filters.CharFilter('services__name', lookup_expr=['exact', 'contains'])
    expired = django_filters.BooleanFilter(method='is_expired')
    # Filters for StaffProfile  /users/?role=2&...
    position_name = django_filters.CharFilter('position__name', lookup_expr=['exact', 'contains'])
    client_id = django_filters.NumberFilter('clients__id')
    clients_id = django_filters.CharFilter(method='get_staff_by_clients')

    def get_staff_by_clients(self, queryset, name, value):
        clients_id_list = value.split(',')
        return queryset.filter(clients__id__in=clients_id_list).distinct()

    def is_expired(self, queryset, name, value):
        if value:
            return queryset.filter(
                (Q(subscription__updated_at__isnull=True) & (
                        Q(subscription__month=1, user__created_at__lt=get_expire_date(month=1)) |
                        Q(subscription__month=6, user__created_at__lt=get_expire_date(month=6)) |
                        Q(subscription__month=12, user__created_at__lt=get_expire_date(month=12)))
                 ) |
                (Q(subscription__updated_at__isnull=False) & (
                        Q(subscription__month=1, subscription__updated_at__lt=get_expire_date(month=1)) |
                        Q(subscription__month=6, subscription__updated_at__lt=get_expire_date(month=6)) |
                        Q(subscription__month=12, subscription__updated_at__lt=get_expire_date(month=12)))
                 )
            )
        else:
            return queryset.filter(
                (Q(subscription__updated_at__isnull=True) & (
                        Q(subscription__month=1, user__created_at__gt=get_expire_date(month=1)) |
                        Q(subscription__month=6, user__created_at__gt=get_expire_date(month=6)) |
                        Q(subscription__month=12, user__created_at__gt=get_expire_date(month=12)))
                 ) |
                (Q(subscription__updated_at__isnull=False) & (
                        Q(subscription__month=1, subscription__updated_at__gt=get_expire_date(month=1)) |
                        Q(subscription__month=6, subscription__updated_at__gt=get_expire_date(month=6)) |
                        Q(subscription__month=12, subscription__updated_at__gt=get_expire_date(month=12)))
                 )
            )


class ServiceFilter(django_filters.FilterSet):
    start_gte = django_filters.TimeFilter('time_start', lookup_expr='gte')
    start_lte = django_filters.TimeFilter('time_start', lookup_expr='lte')

    class Meta:
        model = ServiceModel
        fields = ('name', 'time_start', 'time_end')


class SubscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = SubscriptionModel
        fields = {'month': ['exact'],
                  'updated_at': ['lt', 'gt']}


class PositionFilter(django_filters.FilterSet):
    class Meta:
        model = PositionModel
        fields = {'name': ['exact', 'contains'],
                  'duty': ['exact', 'contains']}
