from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import phonenumbers

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def process_login(request):
    return render(request, 'index.html')

def apply(request):
    return render(request, 'apply_for_access.html')

def process_apply(request):
    if request.method == "GET":
        return redirect('/apply')
    else:
        errors = User.objects.apply_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/apply')
        else:
            #clean up post data for readability
            first_name = request.POST['first_name'].strip()
            first_name = first_name[0].upper() + first_name[1:].lower()
            last_name = request.POST['last_name'].strip()
            last_name = last_name[0].upper() + last_name[1:].lower()
            email = request.POST['email'].strip().lower()
            phone_number = request.POST['phone_number'].strip()
            essay = request.POST['essay'].strip()
            referral = request.POST['referral'].strip()
            try:
                phone_number = phonenumbers.parse(phone_number)
                phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            except:
                messages.error(request, "Please provide your phone number in a valid format")
                return redirect('/apply')
            User.objects.create(first_name = first_name, last_name = last_name, email = email, phone_number = phone_number, essay = essay, referral = referral)
            return redirect('/home')