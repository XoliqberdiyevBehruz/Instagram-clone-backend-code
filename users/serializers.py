from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFED, DONE, PHOTO_STEP
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from shared.utilits import check_email_or_phone_number, send_email, user_input_type
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import serializers
from rest_framework import exceptions
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import update_last_login

class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone_number(user_input) # email or phone
        if input_type == "email":
            data = {
                "email": user_input,
                "auth_type": VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                "phone_number": user_input,
                "auth_type": VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "You must send email or phone number"
            }
            raise ValidationError(data)

        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success": False,
                "message": "Bu email allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "Bu telefon raqami allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)

        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data




class UserChangeInformation(serializers.Serializer):

    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            data = {
                'message':'Password is not much'
            }
            raise ValidationError(data)
        
        if len(password)<8:
            raise ValidationError({
                'message':'Password is too short'
            })
        
        return data
    def validate_username(self, username):
        if len(username) < 3 or len(username) > 31:
            data = {
                'message':'Username is too short'
            }
            raise ValidationError(data)
        if username.isdigit():
            raise ValidationError({
                'message':'This username is entirely numeric.'
            })
        
        return username
    
    def validate_firstname(self, first_name):
        if len(first_name) < 3 or len(first_name) > 31:
            data={
                'message':'Firs name is too short'
            }
            raise ValidationError(data)
        
        return first_name
    
    def validate_last_name(self, last_name):
        if len(last_name) < 3 or len(last_name) > 31:
            data={
                'message':'last_name is too short'
            }
            raise ValidationError(data)
        
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))

        if instance.auth_status == CODE_VERIFED:
            instance.auth_status = DONE
        instance.save()

        return instance
    

class ChangeUserPhoto(serializers.Serializer):
    
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance

class LoginSerializer(TokenObtainPairSerializer):
    
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self,data):
        user_input = data.get('userinput')
        if user_input_type(user_input) == 'username':
            username = user_input

        elif user_input_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username


        elif user_input_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                "message":"Siz email, username yoki telefon raqamini jo'natishiniz kerak"
            }    
            raise ValidationError(data)
        

        authentication_kwargs = {
            self.username_field:username,
            "password":data['password']
        }


        current_user = User.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFED]:
            data = {
                "message":"Siz royxatdan oxirgacha o'tmagansiz"
            }
            raise ValidationError(data)

        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user

        else:
            raise ValidationError(
                {
                    "message":"Sorry, login or password you entered is incorrect. Please check and trg again!"
                }
            )
        user = authenticate(**authentication_kwargs)

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            raise PermissionDenied("Siz login qila olmaysiz. Ruxsatingiz yoq")
        
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data["full_name"] = self.user.full_name

        return data


    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "message":"No active account found"
                }
            )
        return users.first()


class LoginRefreshToken(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data["access"])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()



class ForgotPasswordSerializer(serializers.Serializer):

    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get("email_or_phone", None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success":False,
                    "message":"Email yoki telefon raqamini kiritish kerak"
                }
            )
        
        user = User.objects.filter(Q(email=email_or_phone)|Q(phone_number=email_or_phone))
        if not user.exists():
            raise NotFound(
                {
                    "message":"User not found"
                }
            )
        attrs['user'] = user.first()
        return attrs
    
# class ResetPasswordSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     password = serializers.CharField(min_length=8, write_only=True, required=True)
#     confirm_password = serializers.CharField(min_length=8, write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'password',
#             'confirm_password',
#         )

#    

#  

class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

    # def validate(self, data):
    #     password = data.get('password', None)
    #     confirm_password = data.get('password', None)
    #     if password != confirm_password:
    #         raise ValidationError(
    #             {
    #                 'success': False,
    #                 'message': "Parollaringiz qiymati bir-biriga teng emas"
    #             }
    #         )

    #     return data
    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "message":"Parolingiz bir-biriga mos emas"
                }
            )
        return data


    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)