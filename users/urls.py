from django.urls import path
from .views import CreateUserView, VerifyAPIView, GetNewVerification, UserChangeInformationView, ChangeUserPhotoView

urlpatterns = [
    path('singup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verification/', GetNewVerification.as_view()),
    path('user-done/', UserChangeInformationView.as_view()),
    path('user-done-photo/', ChangeUserPhotoView.as_view())
]
