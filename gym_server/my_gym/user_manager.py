from django.contrib.auth.base_user import BaseUserManager

from . import models


class UserManager(BaseUserManager):
    def create(self, first_name, last_name,  email, role, password=None):

        if first_name is None:
            raise TypeError('User must have a first name.')

        if last_name is None:
            raise TypeError('User must have a last name.')

        if email is None:
            raise TypeError('User must have an email address.')

        user = self.model(first_name=first_name, last_name=last_name, email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, role, password):

        if password is None:
            raise TypeError('Superuser must have a password.')

        superuser = self.create(first_name, last_name, email, role, password=password)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.role = 0
        superuser.save()

        return superuser
