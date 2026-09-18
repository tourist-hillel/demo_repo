from django.contrib import admin
from user_account.models import EventUser
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

# admin.site.unregister(User)
admin.site.register(EventUser)
# Register your models here.
admin.site.register(ContentType)
admin.site.register(Permission)
