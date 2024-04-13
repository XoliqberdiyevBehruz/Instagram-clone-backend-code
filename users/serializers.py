from users.models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFED, DONE, PHOTO_STEP
from django.contrib.auth.password_validation import validate_password
from shared.utilits import check_email_or_phone_number, send_email
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework import exceptions
from django.db.models import Q


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

