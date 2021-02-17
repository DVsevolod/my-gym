from django.contrib import admin
from .models import *

admin.site.register(UserModel)
admin.site.register(ServiceModel)
admin.site.register(SubscriptionModel)
admin.site.register(PositionModel)
admin.site.register(ClientProfileModel)
admin.site.register(StaffProfileModel)
