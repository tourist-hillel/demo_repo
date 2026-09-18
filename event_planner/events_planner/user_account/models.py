from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

SUPPORTED_LANGUAGES = [
    ('uk', 'Ukrainian'),
    ('en', 'English')
]

class EventUserManager(BaseUserManager):
    def create_user(self, cell_phone, email, first_name, password=None, **extra_fields):
        if not cell_phone:
            raise ValueError('Cell phone is required')
        if not email:
            raise ValueError('Email is required')
        if not first_name:
            raise ValueError('First name is required')
        email = self.normalize_email(email)
        user = self.model(cell_phone=cell_phone, email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, cell_phone, email, first_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have "is_staff=True"')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have "is_superuser=True"')

        return self.create_user(cell_phone, email, first_name, password, **extra_fields)
   

class EventUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    cell_phone = models.CharField(max_length=10, unique=True, verbose_name='Cell phone')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of birth')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Last name')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True, verbose_name='Profile image')
    is_active = models.BooleanField(default=True, verbose_name='Is active')
    is_staff = models.BooleanField(default=False, verbose_name='Is staff')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date of account creation')
    app_lang = models.CharField(max_length=5, choices=SUPPORTED_LANGUAGES, default='uk', verbose_name='Preffered app language')

    objects = EventUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'cell_phone'
    REQUIRED_FIELDS = ['email', 'first_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        permissions = [
            ('can_set_user_permissions', 'User can add permissions'),
            ('can_see_user_permissions', 'User can see permissions list')
        ]

    def __str__(self) -> str:
        return self.email
