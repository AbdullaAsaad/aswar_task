from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser

from utils.functions import generate_random_otp
from utils.models import Entity


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensetive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensetive_username_field: username})

        # return self.get(email__iexact=username)

    def create_user(self, name, email, password=None, is_verified=False):
        if not email:
            raise ValueError('User must provide email.')
        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.set_password(password)
        user.is_verified = is_verified
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('User must provide email.')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user


class CustomUser(AbstractUser, Entity):
    username = models.NOT_PROVIDED
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=60)
    is_verified = models.BooleanField(default=False)
    gender = models.CharField(max_length=7, null=True)
    phone = models.CharField(max_length=15, null=True)
    birth_date = models.DateField(null=True)
    profile = models.URLField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser


class Otp(models.Model):
    number = models.IntegerField(default=generate_random_otp)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp')

    def __str__(self):
        return f'{self.user} ||| {self.number}'
