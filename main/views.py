from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import phonenumbers, bcrypt

# Create your views here.

def home(request):
    if not 'logged_user' in request.session:
        return redirect('/login')
    return render(request, 'home.html')

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

def verification(request):
    if 'hold_id' not in request.session:
        return redirect('/login')
    return render(request, 'verification.html')

def process_verification(request):
    if request.method == 'GET':
        return redirect('/login')
    if 'logged_user' in request.session:
        return redirect('/home')
    else:
        errors = User.objects.verification_validator(request.POST, request.session['hold_id'])
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/verification')
        else:
            if not request.session['hold_id']:
                return redirect('/login')
            user = User.objects.get(id = request.session['hold_id'])
            del request.session['hold_id']
            request.session['logged_user'] = user.id
            request.session['logged_first_name'] = user.first_name
            request.session['logged_last_name'] = user.last_name
            if 'first' in request.session:
                del request.session['first']
                return redirect('/about')
            else:
                return redirect('/home')

def login(request):
    if 'logged_user' in request.session:
        return redirect('/home')
    if 'hold_id' in request.session:
        return redirect('/verification')
    else:
        return render(request, 'login.html')

def process_login(request):
    if request.method == 'GET':
        return redirect('/login')
    if 'logged_user' in request.session:
        return redirect('/home')
    else:
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/login')
        else:
            password = request.POST['password']
            phone_number = request.POST['phone_number'].strip()
            try:
                phone_number = phonenumbers.parse(phone_number)
                phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            except:
                messages.error(request, "Please provide your phone number in a valid format")
                return redirect('/login')
            user = User.objects.filter(phone_number = phone_number)[0]
            if not user:
                messages.error(request, "No user with this phone number")
                return redirect('/login')
            if not user.password:
                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user.password = pw_hash
                request.session['first'] = "yes"
            user.save() #to regenerate verification code
            request.session['hold_id'] = user.id
            return redirect('/verification')          


def add_about(request):
    return render(request, 'add_about.html')

def process_edit_profile(request):
    pass

def logout(request):
    if 'logged_user' in request.session:
        del request.session['logged_user']
        del request.session['logged_first_name']
        del request.session['logged_last_name']
        
    return redirect('/login')