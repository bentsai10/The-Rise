from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from urllib.request import urlopen
from bs4 import BeautifulSoup
import phonenumbers, bcrypt

# Create your views here.

def index(request):
    return render(request, 'index.html')

def home(request):
    if not 'logged_user' in request.session:
        return redirect('/login')
    context = {
        'spaces': Space.objects.all(),
        'logged_user': User.objects.get(id = request.session['logged_user']),
    }
    if 'current_space' not in request.session:
        request.session['current_space'] = Space.objects.all().order_by('-created_at').first().id
    
    context['current_space'] = Space.objects.get(id = request.session['current_space'])
    context['discussions'] = context['current_space'].discussion_posts.all().order_by('-created_at')

    if 'current_discussion' not in request.session:
        request.session['current_discussion'] = context['current_space'].discussion_posts.all().order_by('-created_at').first().id
    if Discussion.objects.all().count() < 1:
        context['current_discussion'] = ''
    else:
        context['current_discussion'] = Discussion.objects.get(id = request.session['current_discussion'])

    if 'current_discussion_index' not in request.session:
        context['current_discussion_index'] = 0

    context['favorite_spaces'] = context['logged_user'].favorite_spaces.all()

    return render(request, 'home.html', context)

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
            return redirect('/')

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
                return redirect('/edit_profile')
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


def edit_profile(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    context = {
        'user': User.objects.get(id = request.session['logged_user'])
    }
    return render(request, 'edit_profile.html', context)

def process_edit_profile(request):
    if request.method == 'GET':
        return redirect('/edit_profile')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        errors = User.objects.edit_profile_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/edit_profile')
        else:
            user = User.objects.get(id = request.session['logged_user'])
            if request.POST['year']:
                user.year = request.POST['year'].strip()
            else:
                user.year = ""

            if request.POST['department1']:
                department1 = ""
                department1_raw = request.POST['department1'].strip().split(' ')
                for i in range(len(department1_raw)):
                    department1 += department1_raw[i][0].upper() + department1_raw[i][1:].lower()
                    if i != len(department1_raw) - 1:
                        department1 += " "
                user.department1 = department1

            if request.POST['department2']:
                department2 = ""
                department2_raw = request.POST['department2'].strip().split(' ')
                for i in range(len(department2_raw)):
                    department2 += department2_raw[i][0].upper() + department2_raw[i][1:].lower()
                    if i != len(department2_raw) - 1:
                        department2 += " "
                user.department2 = department2

            if request.POST['department2'] and not request.POST['department1']:
                user.department1 = user.department2
                user.department2 = ""

            if 'title' in request.POST:
                title = request.POST['title'].strip()
                title = title[0].upper() + title[1:].lower()
                user.title = title
                
            if len(request.FILES) > 0:
                user = User.objects.get(id = request.session['logged_user'])
                user.profile_picture = request.FILES.getlist('profile_picture')[0]
            user.save()
            if 'first' in request.session:
                del request.session['first']
                return redirect('/home')
            return redirect('/my_profile')

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
        return redirect('/home')
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
        return redirect('/home')
        
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
    subject = 'Welcome to Humanely Digital!'
    message = f'Hi {user.first_name},\n\nWelcome to Humanely Digital! We are so excited to welcome you into our community as we continue to build a new way to engage with high quality information and connect with people online. To complete your signup process, head over to http://localhost:8000/login. See you there!\n\nWarmly,\nThe Humanely Digital Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    send_mail(subject, message, email_from, recipient_list)
    return redirect('/review')

def profile(request, num):
    if 'logged_user' not in request.session:
        return redirect('/login')
    if User.objects.filter(id = num).all().count() < 1:
        return redirect('/home')
    if num == request.session['logged_user']:
        return redirect('/my_profile')
    context = {
        'user': User.objects.get(id = num)
    }
    return render(request, 'profile.html', context)

def my_profile(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    context = {
        'user': User.objects.get(id = request.session['logged_user'])
    }
    return render(request, 'profile.html', context)

def add_space(request):
    #prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session: 
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('/home')
    return render(request, 'add_space.html')

def process_add_space(request):
    if request.method == "GET":
        return redirect('/spaces')
    name = ""
    name_raw = request.POST['name'].strip().split(' ')
    for i in range(len(name_raw)):
        name += name_raw[i][0].upper() + name_raw[i][1:].lower()
        if i != len(name_raw) - 1:
            name += " "
    Space.objects.create(name = name)
    return redirect('/home')



def process_discussion_post (request):
    if request.method == 'GET':
        return redirect('/home')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        errors = Discussion.objects.post_validator(request.POST, request.FILES)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return render(request, 'partials/post_discussion.html')
        else:
            title = request.POST['title'].strip()
            participant_cap = request.POST['participant_cap']
            link = request.POST['link'].strip()
            user = User.objects.get(id = request.session['logged_user'])

            try:
                link_html = urlopen(link).read()
                soup = BeautifulSoup(link_html)
                link_title = soup.title.string
            except:
                link_title = link
            space = Space.objects.get(id = request.session['current_space'])
            Discussion.objects.create(title = title, participant_cap =  participant_cap, link = link, link_title = link_title, audio = request.FILES.getlist('audio_recording')[0], poster = user, space = space)
            return render(request, 'partials/post_discussion.html')

def space(request, network, space):
    if 'logged_user' not in request.session:
        return redirect('/home')
    request.session['current_space'] = space
    context = {
        'current_space': Space.objects.get(id = request.session['current_space'])
    }
    context['discussions'] = context['current_space'].discussion_posts.all().order_by('-created_at')
    return render(request, 'partials/discussion_posts.html', context)


def load_discussion_banner(request):
    if 'logged_user' not in request.session:
        return redirect('/home')
    context = {
        'current_space': Space.objects.get(id = request.session['current_space']),
        'favorite_spaces': User.objects.get(id = request.session['logged_user']).favorite_spaces.all()
    }
    return render(request, 'partials/discussion_banner.html', context)

def load_response_banner(request):
    if 'logged_user' not in request.session:
        return redirect('/home')
    context = {
        'current_discussion': Discussion.objects.get(id = request.session['current_discussion']),
        'current_discussion_index': request.session['current_discussion_index'],
    }
    return render(request, 'partials/response_banner.html', context)


def process_response_post(request):
    if request.method == 'GET':
        return redirect('/home')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        errors = Response.objects.post_validator(request.POST, request.FILES)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return render(request, 'partials/post_discussion.html')
        else:
            if 'link' in request.POST:
                link = request.POST['link'].strip()
                try:
                    link_html = urlopen(link).read()
                    soup = BeautifulSoup(link_html)
                    link_title = soup.title.string
                except:
                    link_title = link
            else:
                link = None
                link_title = None

            user = User.objects.get(id = request.session['logged_user'])
            discussion = Discussion.objects.get(id = request.session['current_discussion'])
            Response.objects.create(link = link, link_title = link_title, audio = request.FILES.getlist('audio_recording')[0], poster = user, discussion = discussion)
            return render(request, 'partials/post_discussion.html')

def load_responses(request, num, num2):
    if 'logged_user' not in request.session:
        return redirect('/login')
    discussion = Discussion.objects.get(id = num)
    request.session['current_discussion'] = num
    request.session['current_discussion_index'] = num2
    context = {
        'current_discussion': discussion,
        'current_discussion_index': request.session['current_discussion_index']
    }
    return render(request, 'partials/response_posts_block.html', context)

def process_favorite_space(request, num):
    
    if 'logged_user' not in request.session:
        print('here')
        return redirect('/login')
    space = Space.objects.get(id = num)
    user = User.objects.get(id = request.session['logged_user'])
    
    if space in user.favorite_spaces.all():
        user.favorite_spaces.remove(space)
    else:
        user.favorite_spaces.add(space)
    context = {
        'spaces': Space.objects.all(),
        'favorite_spaces': user.favorite_spaces.all()
    }
    return render(request, 'partials/spaces_block.html', context)
    