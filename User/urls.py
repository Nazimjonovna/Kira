from django.urls import path
from .views import (PhoneView, codeView, ValidatedcodeView, RegisterUserView, CreateAccDriverView, ChangePasswordView, 
                    VerifyCodeView, ResetPasswordView, ResetPasswordVerifyCode, ResetPasswordConfirm,
                    CreateAccDriverView, AddOrderView, RegisterBrokerView, BrokerListView, RegisterDriveView, DriverListView)    

urlpatterns = [
    path('phone/', PhoneView.as_view(), name='phone'),
    path('code/', codeView.as_view(), name='code'),
    path('validated-code/', ValidatedcodeView.as_view(), name='validated-code'),
    path('acc/driver/', CreateAccDriverView.as_view()),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-verify-code/', ResetPasswordVerifyCode.as_view(), name='reset-password-verify-code'),
    path('reset-password-confirm/', ResetPasswordConfirm.as_view(), name='reset-password-confirm'),
    path('driver/acc/', CreateAccDriverView.as_view(), name='driver-acc'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('order/', AddOrderView.as_view(), name='order'),
    path('broker/', RegisterBrokerView.as_view(), name='broker'),
    path('broker-list/', BrokerListView.as_view(), name='broker-list'),
    path('driver/', RegisterDriveView.as_view(), name='driver'),
    path('driver-list/', DriverListView.as_view(), name='driver-list'),
]