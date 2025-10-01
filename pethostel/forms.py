from django import forms
from .models import EmployeeReg, PetRegistration

class PetForm(forms.ModelForm):
    class Meta:
        model = PetRegistration
        fields = ['name','gender','breed','age','weight','vaccinated','color']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = EmployeeReg
        fields = ['name','gender','email','phone','address','role']
