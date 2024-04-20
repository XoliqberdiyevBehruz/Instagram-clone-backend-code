# FILES 
from users.serializers import ForgotPasswordSerializer, LoginRefreshToken, LoginSerializer, LogoutSerializer, ResetPasswordSerializer, SignUpSerializer, UserChangeInformation, ChangeUserPhoto
from users.models import NEW, VIA_EMAIL, User, CODE_VERIFED, VIA_PHONE
from shared.utilits import check_email_or_phone_number, send_email
from math import e
# REST FRAMEWORK
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.utils.timezone import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions 
# REST FRAMEWORK SIMPLE JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
# DJANGO
from django.core.exceptions import ObjectDoesNotExist



class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer


class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user             # user ->
        code = self.request.data.get('code') # 4083

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh']
            }
        )

    @staticmethod
    def check_verify(user, code):       # 12:03 -> 12:05 => expiration_time=12:05   12:04
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confired=False)
        print(verifies)
        if  verifies.exists():
            verifies.update(is_confired=True)
        else:
            data = {
                "message": "Tasdiqlash kodingiz eskirgan"
            }
            raise ValidationError(data)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFED
            user.save()
        return True
        
class GetNewVerification(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data = {
                'message':'Telefon raqam yoki email notogri kiritilgan!'
            }
            raise ValidationError(data)
        return Response(
            {
                'success':True,
                'message':'Kod qaytatdan yuborildi'
            }
        )


    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confired=False)
        if verifies.exists():
            data = {
                'message':'Kodingiz xali yaroqli. Iltmos biroz kuting.'
            }
            raise ValidationError(data)
        

class UserChangeInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = UserChangeInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UserChangeInformationView, self).update(request, *args, **kwargs)
        data = {
            'success':True,
            'message':'User updated successfully',
            'auth_status':self.request.user.auth_status
        }
        return Response(data, status=200)
    
    def partial_update(self, request, *args, **kwargs):
        super(UserChangeInformation, self).partial_update(request, *args, **kwargs)
        data={
            'success':True,
            'message':'User updated successfully',
            'auth_status':self.request.user.auth_status
        }
        return Response(data, status=200)
    
class ChangeUserPhotoView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request):
        serializer = ChangeUserPhoto(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            data = {
                    'success':True,
                'message':'Rasm muvaffaqiyatli yuklandi'
            }
            return Response(data, status=200)
            
        return Response(serializer.errors, status=400)
    

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success":True,
                "message":"Logged out successfully"
            }
            return Response(data, status=200)
        except TokenError:
            return Response(status=405)

class LoginRefreshTokenView(TokenRefreshView):
    serializer_class = LoginRefreshToken

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get("user")
        if check_email_or_phone_number(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)
        elif check_email_or_phone_number(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)
        
        return Response(
            {
                'success':True,
                'message':"TAsdiqlash kodi muvaffaqiyatli yuborildi",
                'access_token':user.token()['access'],
                'refresh_token':user.token()['refresh'],
                'user_status':user.auth_status,
            }, status=200
        )


class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist:
            raise NotFound(detail="User not found")
        
        return Response({
            "success":True,
            "message":"Kodingiz muvaffaqiyatli o'zgartirildi",
            "access":user.token()['access'],
            "refresh":user.token()['refresh'],
        }, status=200)