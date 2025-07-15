from django.db import models
from rest_framework.exceptions import ValidationError
import random
import string
from django.core.validators import RegexValidator


def generate_order_number(length=8):
    return ''.join(random.choices(string.digits, k=length))


# Create your models here.
Destiny = [
    ('Toshkent', 'Toshkent'),
        ('Navoiy', 'Navoiy'),
        ('Buxoro', 'Buxoro'),
        ('Samarqand', 'Samarqand'),
        ('Jizzax', 'Jizzax'),
        ('Xorazm', 'Xorazm'),
        ('Sirdaryo', 'Sirdaryo'),
        ('Namangan', 'Namangan'),
        ("Farg'ona", "Farg'ona"),
        ('Andijon', 'Andijon'),
        ('Qashqadaryo', 'Qashqadaryo'),
        ('Surxandaryo', 'Surxandaryo'),
        ('Nukus', 'Nukus')
]


OrderStatus = [
    ('pending', 'pending'),
    ('accepted', 'accepted'),
    ('rejected', 'rejected'),
    ('completed', 'completed'),
    ('cancelled', 'cancelled'),
]


Status = [
    ('sinuvchan', 'sinuvchan'),
    ('yonuvchan', 'yonuvchan'),
]


Types = [
    ('shipper', 'shippper'),
    ('broker', 'broker'),
    ('carier', 'carier')
]


Rate = [
    ("1" , 1),
    ("2" , 2),
    ("3" , 3),
    ("4" , 4),
    ("5" , 5)
]


class User(models.Model):
    phone = models.CharField(max_length=255, unique=True, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)  
    gender = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    pasport = models.FileField(upload_to="pasports/", null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    pasport_seria = models.CharField(max_length=200, null=True, blank=True)
    is_who = models.CharField(max_length=200, choices=Types)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    # def main(self):
    #     if self.is_who == "broker":
    #         self.phone not unique
    #     else:
    #         self.phone unique
    

class Validatedcode(models.Model):
    phone_regex = RegexValidator(regex='d{0,9}', message="Telefon raqamini +9989XXXXXXXX kabi kiriting!")
    phone = models.CharField(validators=[phone_regex],max_length=9,unique=True) 
    code = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Kodni kiritishlar soni:')
    validated = models.BooleanField(default=False, help_text="Shaxsiy kabinetingizni yaratishingiz mumkin!")

    def __str__(self):
        return str(self.phone)


class Verification(models.Model):
    STATUS = (
        ('send', 'send'),
        ('confirmed', 'confirmed'),
    )
    phone = models.CharField(max_length=9, unique=True)
    verify_code = models.SmallIntegerField()
    is_verified = models.BooleanField(default=False)
    step_reset = models.CharField(max_length=10, null=True, blank=True, choices=STATUS)
    step_change_phone = models.CharField(max_length=30, null=True, blank=True, choices=STATUS)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} --- {self.verify_code}"
    
    
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    car_model = models.CharField(max_length=255)
    car_number = models.CharField(max_length=255)
    car_color = models.CharField(max_length=255)
    car_year = models.IntegerField()
    car_type = models.CharField(max_length=255)
    car_image = models.ImageField(upload_to='car_images/')
    litsency_driver = models.FileField(upload_to='driver_litsency/')
    tex_litsency = models.FileField(upload_to='tex_litsency/')
    card_number = models.IntegerField()
    card_period = models.IntegerField()
    telegram_nik = models.TextField()
    rate = models.IntegerField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    image = models.FileField(upload_to = 'order_images/')
    descriptions = models.TextField()
    from_place = models.CharField(max_length=255, choices=Destiny)
    to_place = models.CharField(max_length=255, choices=Destiny)
    price = models.IntegerField()
    status = models.CharField(max_length=250, choices=OrderStatus)
    ordertype = models.CharField(max_length=250, choices=Status)
    number = models.CharField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.to_place} - {self.from_place}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = generate_order_number()
        super().save(*args, **kwargs)


class Broker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_address = models.TextField()
    company_phone = models.CharField(max_length=255)
    company_email = models.EmailField()
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    company_description = models.TextField()
    company_website = models.URLField()
    rate = models.IntegerField()
    drivers = models.ManyToManyField(Driver, related_name='brokers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    

# class Contract(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     company = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField(auto_now=True)
#     price = models.FloatField()
#     status = models.CharField(choices=OrderStatus)
#     description = models.TextField()
#     rate = models.IntegerField()