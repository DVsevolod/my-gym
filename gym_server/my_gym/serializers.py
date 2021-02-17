from rest_framework import serializers
from rest_framework.utils import model_meta

from my_gym.models import *
from .utils import check_user_data, check_subscription_data


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'is_active', 'created_at')
        read_only_fields = ('is_active',)


class SubscriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ('id', 'month', 'updated_at')


class ServiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceModel
        fields = ('id', 'name', 'time_start', 'time_end')


class PositionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionModel
        fields = ('id', 'name', 'duty')


class CustomForeignKeyField(serializers.PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        self.model = kwargs.pop('model', None)
        self.serializer = kwargs.pop('serializer', None)
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def get_queryset(self):
        return self.queryset

    def to_representation(self, value):
        value = super().to_representation(value)
        model_object = self.model.objects.get(pk=value)
        return self.serializer(model_object).data


class CustomListFiled(serializers.ListField):
    def to_representation(self, data):
        print(data)
        return [self.child.to_representation(item) if item is not None else None for item in data]


class ClientProfileSerializer(serializers.ModelSerializer):
    user = CustomForeignKeyField(model=UserModel,
                                 serializer=UserModelSerializer,
                                 queryset=UserModel.objects.all())
    subscription = CustomForeignKeyField(model=SubscriptionModel,
                                         serializer=SubscriptionModelSerializer,
                                         queryset=SubscriptionModel.objects.all(),
                                         required=False)
    services = CustomForeignKeyField(model=ServiceModel,
                                     serializer=ServiceModelSerializer,
                                     queryset=ServiceModel.objects.all(),
                                     many=True)
    updated_data = serializers.DictField(required=False)
    subscription_data = serializers.DictField(required=False)

    class Meta:
        model = ClientProfileModel
        fields = ('id', 'user', 'subscription', 'services', 'updated_data', 'subscription_data')


    def create(self, validated_data):
        user = validated_data.get('user', None)
        subscription_data = validated_data.get('subscription_data', None)
        services = validated_data.get('services', None)

        try:
            client_profile_exist_check = ClientProfileModel.objects.get(user=user)
            raise serializers.ValidationError('This client profile already exists.')
        except ClientProfileModel.DoesNotExist:
            pass

        if subscription_data is None:
            subscription = SubscriptionModel.objects.create()
        else:
            subscription = SubscriptionModel.objects.create(**subscription_data)
        client_profile = ClientProfileModel.objects.create(user=user, subscription=subscription)
        for service in services:
            client_profile.services.add(service)

        return client_profile

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        user = instance.user
        subscription = instance.subscription
        services = validated_data.get('services', None)

        updated_data = validated_data.get('updated_data', None)

        if updated_data:
            user_data = updated_data.get('user', None)
            subscription_data = updated_data.get('subscription', None)

            if user_data:
                check_user_data(user_data)
                password = user_data.get('password', None)
                if password:
                    user.set_password(password)

                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()
            else:
                user = user_data

            if subscription_data:
                check_subscription_data(subscription_data)
                for attr, value in subscription_data.items():
                    setattr(subscription, attr, value)
                subscription.save()
            else:
                subscription = subscription_data

        client_profile_data = {"user": user, "subscription": subscription, "services": services}

        m2m_fields = []
        for attr, value in client_profile_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                if value:
                    setattr(instance, attr, value)

        instance.save()

        if services:
            for attr, value in m2m_fields:
                field = getattr(instance, attr)

                field.set(value)

        return instance


class StaffProfileSerializer(serializers.ModelSerializer):
    user = CustomForeignKeyField(model=UserModel,
                                 serializer=UserModelSerializer,
                                 queryset=UserModel.objects.all())
    position = CustomForeignKeyField(model=PositionModel,
                                 serializer=PositionModelSerializer,
                                 queryset=PositionModel.objects.all())
    clients = CustomForeignKeyField(model=UserModel,
                                     serializer=UserModelSerializer,
                                     queryset=UserModel.objects.all(),
                                     many=True)
    updated_data = serializers.DictField(required=False)

    class Meta:
        model = StaffProfileModel
        fields = ('id', 'user', 'position', 'clients', 'updated_data')

    def create(self, validated_data):
        user = validated_data.get('user', None)
        position = validated_data.get('position', None)
        clients = validated_data.get('clients', None)

        try:
            staff_profile_exist_check = StaffProfileModel.objects.get(user=user)
            raise serializers.ValidationError('This staff profile already exists.')
        except StaffProfileModel.DoesNotExist:
            pass

        staff_profile = StaffProfileModel.objects.create(user=user, position=position)
        for client in clients:
             staff_profile.clients.add(client)

        return staff_profile

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        user = instance.user
        position = validated_data.get('position', None)
        clients = validated_data.get('clients', None)
        updated_data = validated_data.get('updated_data', None)

        if updated_data:
            user_data = updated_data.get('user', None)

            if user_data:
                check_user_data(user_data)
                password = user_data.get('password', None)
                if password:
                    user.set_password(password)

                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()
            else:
                user = user_data

        staff_profile_data = {"user": user, "position": position, "clients": clients}

        m2m_fields = []
        for attr, value in staff_profile_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                if value:
                    print(attr, value)
                    setattr(instance, attr, value)

        instance.save()

        if clients:
            for attr, value in m2m_fields:
                field = getattr(instance, attr)
                field.set(value)

        return instance
