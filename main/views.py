from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import phonenumbers, bcrypt

# Create your views here.

def index(request):
    return render(request, 'index.html')

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

def review_redir(request):
    #prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session:
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('home')
    #generic link, so get the latest unapproved application from users
    if User.objects.filter(status = False).all().count() > 0:
        min = User.objects.filter(status = False).all().first().id
        return redirect('/review/{}'.format(min))
    # accounts for case no applications left
    else:
        context = {
            'empty': True
        }
        return render(request, 'review.html', context)

def review(request, num):
    #prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session: 
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('home')
        
    #if user id doesn't exist or already been approved, redirect
    if User.objects.filter(id = num).all().count() < 1:
        return redirect('/review')
    
    user = User.objects.get(id = num)
    if user.status == True:
        return redirect('/review')
    
    context = {
        'applicant': user
    }
    greater_than = User.objects.filter(status = False, id__gt = user.id).all()
    less_than = User.objects.filter(status = False, id__lt = user.id).all()
    if greater_than.count() > 0:
        context['next_user'] = greater_than.first()
    if less_than.count() > 0:
        context['previous_user'] = less_than.last()
    return render(request, 'review.html', context)

def process_approve(request):
    if request.method == 'GET':
        return redirect('/review')
    id = request.POST['id']
    user = User.objects.get(id = id)
    user.status = True
    user.save()
    return redirect('/review')