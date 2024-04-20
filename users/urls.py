from django.urls import path
from .views import CreateUserView, LoginView, VerifyAPIView, GetNewVerification, UserChangeInformationView, ChangeUserPhotoView, LoginRefreshTokenView, LogoutView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('login/refresh/', LoginRefreshTokenView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('singup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verification/', GetNewVerification.as_view()),
    path('user-done/', UserChangeInformationView.as_view()),
    path('user-done-photo/', ChangeUserPhotoView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]
