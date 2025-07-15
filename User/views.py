from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from random import randint
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (Userserializer, DriverSerializer, PhoneSerializer, SMSCodeSerializer, 
                          ChangePasswordSerializer, VerifyCodeSerializer, ResetPasswordSerializer, 
                          OrderSerializer, BrokerSerializer, UserLoginSerializer,
                          FilterOrderSerializer)
from .models import User, Driver, Validatedcode, Verification, Broker, Order
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# from get_sms import Getsms
import datetime as d
import pytz
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



utc = pytz.timezone(settings.TIME_ZONE)
min = 1
def send_sms(phone_number, step_reset=None, change_phone=None):
    try:
        verify_code = randint(1111, 9999)
        try:
            obj = Verification.objects.get(phone=phone_number)
        except Verification.DoesNotExist:
            obj = Verification(phone=phone_number, verify_code=verify_code)
            obj.step_reset=step_reset 
            obj.step_change_phone=change_phone
            obj.save()
            context = {'phone_number': str(obj.phone), 'verify_code': obj.verify_code,
                       'lifetime': _(f"{min} minutes")}
            return context
        time_now = d.datetime.now(utc)
        diff = time_now - obj.created
        three_minute = d.timedelta(minutes=min)
        if diff <= three_minute:
            time_left = str(three_minute - diff)
            return {'message': _(f"Try again in {time_left[3:4]} minute {time_left[5:7]} seconds")}
        obj.delete()
        obj = Verification(phone=phone_number)
        obj.verify_code=verify_code 
        obj.step_reset=step_reset
        obj.step_change_phone=change_phone
        obj.save()
        context = {'phone_number': str(obj.phone), 'verify_code': obj.verify_code, 'lifetime': _(f"{min} minutes")}
        return context
    except Exception as e:
        print(f"\n[ERROR] error in send_sms <<<{e}>>>\n")



class PhoneView(APIView):
    queryset = User.objects.all()
    serializer_class = PhoneSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PhoneSerializer, tags = ['Register'])
    def post(self, request, *args, **kwargs):
        phone_number = str(request.data.get("phone"))
        if phone_number.isdigit() and len(phone_number)>8:
            user = User.objects.filter(phone__iexact=phone_number)
            if user.exists():
                return Response({
                    "status": False,
                    "detail": "Bu raqam avval registerdan otgan."
                })
            else:
                code = send_sms(phone_number)
                if 'verify_code' in code:
                    code = str(code['verify_code'])
                    try:
                        validate = Validatedcode.objects.get(phone=phone_number)
                        if validate.validated:
                            validate.code = code
                            validate.validated= False
                            validate.save()
                        
                    except Validatedcode.DoesNotExist as e:
                        phon = Validatedcode.objects.filter(phone__iexact=phone_number)
                        print("expect")
                        if not phon.exists():
                            Validatedcode.objects.create(phone=phone_number, code=code, validated=False)
                        else:
                            Response({"phone": "mavjud"})

                return Response({
                    "status": True,
                    "detail": "SMS xabarnoma jo'natildi",
                    "code":code 
                })
        else:
            if len(phone_number)<8:
                return Response({"detail":"Telefon raqamingizni kod bilan kiriting!"})
            else:    
                return Response({
                    "status": False,
                    "detail": "Telefon raqamni kiriting ."
                })


    def send_code(phone, code):
        if phone:
            code = randint(999, 9999)
            print(code)
            return code
        else:
            return False


class codeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SMSCodeSerializer, tags = ['Register'])
    def post(self, request):
        phone_number = request.data.get('phone', True)
        code_send = request.data.get('code', True)
        if not phone_number and code_send:
            return Response({
                    'status': False,
                    'detail': 'codeni va phone ni kiriting'
                })

        try:
            verify = Validatedcode.objects.get(phone=phone_number, validated=False)
            if verify.code == code_send:
                    verify.count += 1
                    verify.validated = True
                    verify.save()

                    return Response({
                        'status': True,
                        'detail': "code to'g'ri"
                        })
            else:
                return Response({
                   'status': False,
                   'error': "codeni to'g'ri kiriting"})
            
        except Validatedcode.DoesNotExist as e:
            return Response({
               'error': "code aktiv emas yoki mavjud emas, boshqa code oling"
            })

        


class ValidatedcodeView(APIView):
    @swagger_auto_schema(tags=['User'])
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        code_sent = request.data.get('code', False)

        if phone and code_sent:
            old = Validatedcode.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                code = old.code
                if str(code_sent) == str(code):
                    old.validated = True
                    old.save()   
                    return Response({
                        'status': True,
                        'detail': "code to'g'ri"
                        })
                else:
                    return Response({
                        'status': False,
                        'detail': "code noto'g'ri"
                        })
            else:
                return Response({
                    'status': False,
                    'detail': "code aktiv emas yoki mavjud emas, boshqa code oling"
                    })

@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = Userserializer
    parser_classes = [MultiPartParser, FileUploadParser]

    @swagger_auto_schema(request_body=Userserializer, tags=['User'])
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                phone = serializer.validated_data.get('phone')
                password = serializer.validated_data.get('password')
                code = serializer.validated_data.get('code')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                gender = request.data.get('gender')
                birth_date = request.data.get('birth_date')
                address = request.data.get('address')
                city = request.data.get('city')
                country = request.data.get('country')
                postal_code = request.data.get('postal_code')
                pasport = request.data.get('pasport')
                pasport_seria = request.data.get('pasport_seria')
                is_who = request.data.get('is_who')
                verify = Validatedcode.objects.filter(phone__iexact=phone, validated=True)
                if not verify.exists():
                    return Response({
                        "status": False,
                        "detail": _("You haven't entered a valid one-time secret code. Therefore, you cannot proceed with registration.")
                    }, status=status.HTTP_400_BAD_REQUEST)

                hashed_password = make_password(password)
                user_obj = User.objects.create(phone=phone, password=hashed_password, code=code, first_name=first_name,
                                               gender=gender, birth_date=birth_date, address=address,
                                               city=city, country=country, postal_code=postal_code,
                                               pasport=pasport, pasport_seria=pasport_seria, is_who=is_who)

                access_token = AccessToken().for_user(user_obj)
                refresh_token = RefreshToken().for_user(user_obj)

                return Response({
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                    "phone": str(user_obj.phone),
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({
                "status": False,
                "detail": _("An error occurred while processing your request.")
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Userserializer
    parser_classes = [MultiPartParser, FileUploadParser]

    @swagger_auto_schema(tags=['User'])
    def get(self, pk, request, *arg, **kwargs):
        user = User.objects.filter(id = pk)
        if user.exists():
            serialiser = Userserializer(user, many = True)
            return Response({
                "user":serialiser.data,
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "message":'User not found',
                "status":status.HTTP_200_OK
            })

    @swagger_auto_schema(tags=['User'])    
    def delete(self, pk, request):
        user = User.objects.filter(id = pk)
        if user.exists():
            user.delete()
            return Response({
                "message":"User deleted Successfully",
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "message":'User not found',
                "status":status.HTTP_200_OK
            })
        
    @swagger_auto_schema(request_body=Userserializer, tags=["User"])
    def patch(self, pk, request, *args, **kwargs):
        user = User.objects.filter(id = pk)
        if user.exists():
            serializer = Userserializer(instanse = user, data =request.data, parial = True)
            serializer.save()
            return Response({
                "user":serializer.data,
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "message":'User not found',
                "status":status.HTTP_200_OK
            })
        


class ChangePasswordView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(request_body=ChangePasswordSerializer, tags = ['User'])
    def put(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Password successfully updated'}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]
    queryset = Verification.objects.all()

    @swagger_auto_schema(request_body=VerifyCodeSerializer, tags=['User'])
    def put(self, request, *args, **kwargs):
        data = request.data
        try:
            obj = Verification.objects.get(phone=data['phone'])
            serializer = VerifyCodeSerializer(instance=obj, data=data)
            if serializer.is_valid():
                serializer.save()
                if serializer.data['step_change_phone'] == 'confirmed':
                    user = request.user
                    user.phone = data['phone']
                    user.save()
                    return Response({'message': 'Your phone number has been successfully changed!'},
                                status=status.HTTP_202_ACCEPTED)
                return Response({'message': 'This phone number has been successfully verified!'},
                                status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Verification.DoesNotExist:
            return Response({'error': 'Phone number or verify code incorrect!'}, statusis_pupil=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    @swagger_auto_schema(request_body=PhoneSerializer, tags=['User'])
    def post(self, request):
        data = request.data
        if data.get('phone'):
            phone = data['phone']
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                user = user.first()
                context = send_sms(phone)
                return Response(context, status=status.HTTP_208_ALREADY_REPORTED)
            return Response({'msg': _('User not found!')})
        return Response({'msg': _("Enter phone number")}, status=status.HTTP_400_BAD_REQUEST)    


class ResetPasswordVerifyCode(VerifyCodeView):
    my_tags = ['User']


class ResetPasswordConfirm(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(request_body=ResetPasswordSerializer, tags=['User'])
    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.get(phone=request.data['phone'])
        except:
            return Response({'error': "User matching query doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResetPasswordSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            ver = Verification.objects.get(phone=request.data['phone'])
            user.set_password(request.data['new_password'])
            ver.step_reset = ''
            ver.save()
            user.save()
            return Response({'message': 'Password successfully updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterBrokerView(APIView):
    permission_classes = [AllowAny]
    serializer_class = BrokerSerializer
    parser_classes = [MultiPartParser, FileUploadParser]

    @swagger_auto_schema(request_body=BrokerSerializer, tags=['Broker'])
    def post(self, request, *args, **kwargs):
        serializer = BrokerSerializer(data=request.data)
        user = User.objects.filter(id=request.data['user'])
        if user.exists():
            if serializer.is_valid():
                serializer.save()
                access_token = AccessToken().for_user(user)
                refresh_token = RefreshToken().for_user(user)
                return Response({
                    "status":status.HTTP_200_OK,
                    "broker":serializer.data,
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                    "phone": str(user.phone),
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        

class BrokerListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BrokerSerializer
    parser_classes = [MultiPartParser, FileUploadParser]

    @swagger_auto_schema(tags=['Broker'])
    def get(self, pk, request, *args, **kwargs):
        broker = Broker.objects.filter(id = pk)
        user = User.objects.filter(id=broker.user)
        serializer = BrokerSerializer(broker, many=True)
        serialiser_user = Userserializer(user, many=True)
        return Response({'broker' : str(serializer.data),
                         "user" : str(serialiser_user.data),
                          'status':str(status=status.HTTP_200_OK)}) 
    
    @swagger_auto_schema(tags=['Broker'])
    def delete(self, request, *args, **kwargs):
        broker = Broker.objects.get(id=kwargs['pk'])
        user = User.objects.filter(id=broker.user.id)
        broker.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(request_body=BrokerSerializer, tags=['Broker'])
    def put(self, request, *args, **kwargs):
        broker = Broker.objects.get(id=kwargs['pk'])
        serializer = BrokerSerializer(instance=broker, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateAccDriverView(APIView):
    parser_classes = [MultiPartParser, FileUploadParser]
    permission_classes = [AllowAny]
    serializer_class = DriverSerializer

    @swagger_auto_schema(request_body=DriverSerializer, tags = ['Driver'])
    def post(self, request,  *args, **kwargs):
        serializer = DriverSerializer(data = request.data)
        user = User.objects.filter(id=request.data['user'])
        if user.exists():
            if serializer.is_valid():
                serializer.save()
                access_token = AccessToken().for_user(user)
                refresh_token = RefreshToken().for_user(user)
                return Response({
                    "status":status.HTTP_200_OK,
                    "driver":serializer.data,
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                    "phone": str(user.phone),
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
            

class DriverListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverSerializer
    parser_classes = [MultiPartParser, FileUploadParser]

    @swagger_auto_schema(tags=['Driver'])
    def get(self, pk, request, *args, **kwargs):
        driver = Driver.objects.filter(id=pk)
        user = User.objects.get(id=driver.user)
        serializer = DriverSerializer(driver, many=True)
        serialiser_user = Userserializer(user, many=True)
        return Response({'driver' : str(serializer.data),
                         "user" : str(serialiser_user.data),
                          'status':str(status=status.HTTP_200_OK)}) 
        
    @swagger_auto_schema(tags=['Driver'])
    def delete(self, request, *args, **kwargs):
        driver = Driver.objects.get(id=kwargs['pk'])
        user = User.objects.filter(id=driver.user.id)
        driver.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(request_body=DriverSerializer, tags=['Driver'])
    def put(self, request, *args, **kwargs):
        driver = Driver.objects.get(id=kwargs['pk'])
        serializer = DriverSerializer(instance=driver, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(request_body=UserLoginSerializer, tags=['User'])
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = User.objects.filter(phone__iexact=phone)
        if user.exists():
            user = user.first()
            if check_password(password, user.password):
                access_token = AccessToken().for_user(user)
                refresh_token = RefreshToken().for_user(user)
                return Response({
                    'message': 'Login successful',
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                    "phone": str(user.phone),
                })
        return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)
    


class AddOrderView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    serializer_class = OrderSerializer

    @swagger_auto_schema(request_body=OrderSerializer, tags=['Order'])
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    serializer_class = OrderSerializer

    @swagger_auto_schema(tags=['Order'])
    def get(self, pk, request, *args, **kwargs):
        order = Order.objects.filter(id = pk)
        if order.exists():
            serializer = OrderSerializer(order)
            return Response({
                "order":serializer.data,
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "message":"Order not found",
                "status":status.HTTP_200_OK
            })

    @swagger_auto_schema(tags=['Order']) 
    def delete(self, pk, request):
        order = Order.objects.filter(id = pk)
        if order.exists():
            order.delete()
            return Response({
                "message":"Order deleted successfully",
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "message":"Order not found",
                "status":status.HTTP_200_OK
            })
        
    @swagger_auto_schema(request_body=OrderSerializer, tags=['Order'])
    def patch(self, pk, request, *args, **kwargs):
        order = Order.objects.filter(id = pk)
        if order.exists():
            serializer = OrderSerializer(instanse = order, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "order":serializer.data,
                    "status":status.HTTP_200_OK,
                    'messege':'order updated successfully'
                })
            else:
                return Response ({
                    'error':serializer.errors,
                    'status':status.HTTP_200_OK
                })
        else:
            return Response({
                    'messege':'order not found',
                    'status':status.HTTP_200_OK
            })
        

class FilterOrderView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = FilterOrderSerializer

    def post(self, request, *args, **kwargs):
        orders = []
        from_place = request.data['from_place']
        to_place = request.data['to_place']
        orders_from = Order.objects.filter(from_place = from_place)
        order_to = Order.objects.filter(to_place = to_place)
        if order_to.status == "pending" and orders_from.status == "pending":
            orders.append(orders_from)
            orders.append(orders_from)
            serializer = OrderSerializer(orders, many = True)
            return Response({
                "msg": "Saralangan buyurtmalar",
                "orders":serializer.data,
                "status":status.HTTP_200_OK
            })
        else:
            return Response({
                "msg":"Bunday manzil bo'yicha buyurtmalar topilmadi",
                "status":status.HTTP_200_OK
            })
        
