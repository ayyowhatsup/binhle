#
# (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
#
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
# Create your models here.
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("You have not provided a valid email address")
        
        email = self.normalize_email(email)
        user = self.model(email = email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, email = None, password = None , **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)

        return self._create_user(email, password, **kwargs)
    
    def create_superuser(self, email = None, password = None , **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self._create_user(email, password, **kwargs)
    
class User(AbstractBaseUser, PermissionsMixin):

    class Meta:
        db_table = "Users"
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, default='', blank=True)
    phone_number = models.CharField(max_length=15, default='', blank=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_oauth = models.BooleanField(default=False)
    
    last_login = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self) -> str:
        return self.email



