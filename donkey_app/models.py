import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True, null=False)
    email = models.EmailField(max_length=200, unique=True, null=False)
    password = models.CharField(max_length=200, null=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username}, {self.email}'


class Chat(models.Model):
    chat_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner}: {self.chat_id}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}: {self.content[:50]}...'