from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class PetRegistration(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=8, choices=[('Male','Male'),('Female','Female')])
    breed =models.CharField(max_length=20)
    age = models.IntegerField()
    weight = models.FloatField()
    vaccinated = models.BooleanField()
    color = models.CharField(max_length=40)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EmployeeReg(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=8, choices=[('Male','Male'),('Female','Female')])
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    role =models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    category = models.CharField(max_length=10, primary_key=True ,choices=[('Normal', 'Normal'),('Standard', 'Standard'),('Premium', 'Premium'),])
    capacity = models.IntegerField()
    price = models.IntegerField()
    total_rooms = models.IntegerField()


class Booking(models.Model):
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_pets = models.IntegerField()
    room_category =  models.CharField(max_length=10, choices=[('Normal', 'Normal'),('Standard', 'Standard'),('Premium', 'Premium')], default='Normal' )
    cost = models.IntegerField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    pets = models.CharField(max_length=100,default=None)
    cost = models.IntegerField()
