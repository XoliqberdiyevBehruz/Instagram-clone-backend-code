from django.core.validators import FileExtensionValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from shared.models import BaseModel
from django.db import models
import random
import uuid


PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5
ORDINARY_USER, MANAGER, ADMIN = ('ordinary_user', 'manager', 'admin')
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')
NEW,CODE_VERIFED,DONE,PHOTO_STEP = ('new', 'code_verifed', 'done', 'photo_step')

# CLASS ABOUT USERS 
class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFED, CODE_VERIFED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )


    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(max_length=31, null=True, unique=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, unique=True, blank=True)
    photo = models.ImageField(upload_to='users_profile_photo/', null=True, blank=True,validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    def create_verify_code(self, verify_type):
        code = ''.join([str(random.randint(0, 100)%10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id = self.id,
            verify_type = verify_type,
            code = code
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f'{temp_username}{random.randint(0,100)}'
            self.username = temp_username


    def check_email(self):
        if self.email:
            normalize = self.email.lower()
            self.email = normalize


    def check_pass(self):
        if not self.password:
            temp_password = f'password-{uuid.uuid4().__str__().split("-")[-1]}'
            self.password = temp_password


    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_password()
        

    def save(self,  *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)


# CLASS ABOUT USERCONFIRMATIONS
class UserConfirmation(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )


    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=31, choices=VERIFY_TYPE)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())


    def save(self, *args, **kwargs):
        if self.verify_type == VIA_PHONE:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)