from django.contrib import admin
from django.contrib.auth import get_user_model

from account.models import Otp

User = get_user_model()

admin.site.register(User)
admin.site.register(Otp)
