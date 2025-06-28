from django.urls import path
from .views import (PhoneView, codeView, ValidatedcodeView, RegisterUserView, CreateAccDriverView, ChangePasswordView, 
                    VerifyCodeView, ResetPasswordView, ResetPasswordVerifyCode, ResetPasswordConfirm,
                    CreateAccDriverView, AddOrderView, RegisterBrokerView, BrokerListView, DriverListView,
                    UserLoginView, UserDetailView, OrderDetailView)    

urlpatterns = [
    path('phone/', PhoneView.as_view(), name='phone'),
    path('code/', codeView.as_view(), name='code'),
    path('validated-code/', ValidatedcodeView.as_view(), name='validated-code'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('user/acc/<int:pk>/', UserDetailView.as_view()),
    path('driver/acc/', CreateAccDriverView.as_view(), name='driver-acc'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('broker/', RegisterBrokerView.as_view(), name='broker'),
    path('broker-list/<int:pk>/', BrokerListView.as_view(), name='broker-list'),
    path('driver-list/<int:pk>/', DriverListView.as_view(), name='driver-list'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-verify-code/', ResetPasswordVerifyCode.as_view(), name='reset-password-verify-code'),
    path('reset-password-confirm/', ResetPasswordConfirm.as_view(), name='reset-password-confirm'),
    path('order/', AddOrderView.as_view(), name='order'),
    path('order/update/<int:pk>/', OrderDetailView.as_view())
]