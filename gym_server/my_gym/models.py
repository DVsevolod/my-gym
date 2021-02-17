from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

import jwt

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from django.db import models

from .user_manager import UserManager


class UserModel(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(db_index=True, unique=True)
    role = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def access_token(self):
        return self._generate_access_token()

    @property
    def refresh_token(self):
        return self._generate_refresh_token()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return f"{self.first_name[0]}.{self.last_name}"

    def _generate_access_token(self):
        date = datetime.now() + timedelta(hours=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': date
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    def _generate_refresh_token(self):
        date = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.pk,
            'refresh': 0,
            'exp': date
        }, settings.SECRET_KEY, algorithm='HS256')

        return token


class TokenModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email


class SubscriptionModel (models.Model):
    MONTHS_LIMITATIONS = [(1, '1 month'),
                          (6, '6 months',),
                          (12, '12 months',)]
    month = models.IntegerField(choices=MONTHS_LIMITATIONS, default=1)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"pk {self.pk}"


class PositionModel(models.Model):
    name = models.CharField(max_length=255)
    duty = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ServiceModel(models.Model):
    name = models.CharField(max_length=255)
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        return self.name


class ClientProfileModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    subscription = models.ForeignKey(SubscriptionModel, on_delete=models.CASCADE)
    services = models.ManyToManyField(ServiceModel)

    @property
    def is_expired(self):
        if self.subscription.updated_at is None:
            expired = self.create_expired(self.user.created_at)
        else:
            expired = self.create_expired(self.subscription.updated_at)
        if datetime.now().date() >= expired:
            return True
        return False

    def create_expired(self, date):
        expired = date + relativedelta(months=self.subscription.month)
        return expired

    def __str__(self):
        return self.user.email


class StaffProfileModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='staff')
    position = models.ForeignKey(PositionModel, on_delete=models.CASCADE)
    clients = models.ManyToManyField(UserModel, related_name='clients')
