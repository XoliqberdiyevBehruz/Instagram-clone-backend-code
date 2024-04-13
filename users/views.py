from users.serializers import SignUpSerializer, UserChangeInformation, ChangeUserPhoto
from users.models import NEW, VIA_EMAIL, User, CODE_VERIFED, VIA_PHONE
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.utils.timezone import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions 
from shared.utilits import send_email
from math import e



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