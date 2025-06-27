from django.contrib import admin
from .models import User, Driver, Customer, Order, Validatedcode, Verification

admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Validatedcode)
admin.site.register(Verification)

# Register your models here.
