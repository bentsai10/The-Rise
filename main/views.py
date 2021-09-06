from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q, Count
from urllib.request import urlopen
from bs4 import BeautifulSoup
import phonenumbers, bcrypt, dotenv, os
from twilio.rest import Client



# Render landing page
def index(request):
    return render(request, 'index.html')

# Render home page
def home(request):
    # If no logged in user, redirect to login page
    if not 'logged_user' in request.session:
        return redirect('/login')

    # Since there is a user, let's provide the context for the profile section in the upper right and the spaces for 'all spaces'
    context = {
        'spaces': Space.objects.all().order_by('name'),
        'logged_user': User.objects.get(id = request.session['logged_user']),
    }

    user = context['logged_user']

    # If no space is currently selected, 
    # We assign the id of The Rise space
    if 'current_space' not in request.session:
        request.session['current_space'] = 2
    
    # Now that we have the id of the current space, let's supply it to context
    # We will also supply all of the discussions within that space to context
    context['current_space'] = Space.objects.get(id = request.session['current_space'])
    context['discussions'] = context['current_space'].discussion_posts.all().order_by('-created_at')

    # If no discussion is currently selected,
    # We assign the id of the most recent discussion in the space as the current discussion
    # If there are no discussions in the space, we assign None
    if 'current_discussion' not in request.session or request.session['current_discussion'] == None:
        if context['current_space'].discussion_posts.all().count() > 0:
            request.session['current_discussion'] = context['current_space'].discussion_posts.all().order_by('-created_at').first().id
        else:
            request.session['current_discussion'] = -1
    if request.session['current_discussion'] == -1:
        context['current_discussion'] = -1
    else:        
        print(request.session['current_discussion'])
        context['current_discussion'] = Discussion.objects.get(id = request.session['current_discussion'])
    # Current discussion index resembles the playlist name of the current discussion for integration w/ Amplitude JS
    # If no discussion is currently selected, we assign -1, which will never match a playlist in Amplitude JS
    if 'current_discussion_index' not in request.session:
        context['current_discussion_index'] = -1
    else:
        context['current_discussion_index'] = request.session['current_discussion_index']

    # Provide the logged in user's favorite spaces to context
    context['favorite_spaces'] = context['logged_user'].favorite_spaces.all()

    # At this point, context contains:
    # 1) 'spaces': all the spaces, 2) 'logged_user': id of the logged in user, 3) 'current_space': the currently selected space,
    # 4) 'discussions': all discussions within the currently selected space, 5) 'current_discussion': the currently selected discussion,
    # 6) 'current_discussion_index': the corresponding playlist name of the currently selected discussion,
    # 7) 'favorite_spaces': all the favorite spaces of the logged in user

    for key in list(request.session.keys()):
            print(key, request.session[key])

    return render(request, 'home.html', context)

# Render application page
def apply(request):
    return render(request, 'apply_for_access.html')

# Processing a submitted application
def process_apply(request):
    # if request not sent from a form submission, redirect them back to the application page
    if request.method == "GET":
        return redirect('/apply')
    else:
        # Validate submitted data using the appropriate validator for the User object in models.py
        errors = User.objects.apply_validator(request.POST)

        # If there are errors, redirect them to apply page with error messages
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/apply')
        else:
            # Clean up post data for readability and data uniformity
            first_name = request.POST['first_name'].strip()
            first_name = first_name[0].upper() + first_name[1:].lower()
            last_name = request.POST['last_name'].strip()
            last_name = last_name[0].upper() + last_name[1:].lower()
            email = request.POST['email'].strip().lower()
            phone_number = request.POST['phone_number'].strip()
            essay = request.POST['essay'].strip()
            referral = request.POST['referral'].strip()

            # Use phonenumbers module to parse phone number from response and convert it to E164 format for Twilio
            try:
                phone_number = phonenumbers.parse(phone_number)
                phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            except:
                messages.error(request, "Please provide your phone number in a valid format")
                return redirect('/apply')
            
            # If everything works, create User in database with cleaned values + converted phone number
            User.objects.create(first_name = first_name, last_name = last_name, email = email, phone_number = phone_number, essay = essay, referral = referral)

            # Redirect them to landing page, b/c they're not yet approved for login
            return redirect('/')

# Twilio setup for 2-step verification
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# Render page for entering 2-step code
def verify(request):
    # If no id is being held (meaning no successful login yet), redirect to login page
    if 'hold_id' not in request.session:
        return redirect('/login')
    return render(request, 'verification.html')

# Process submitted verification code
def process_verification(request):
    # If no id is being held (meaning no successful login yet) or if request not sent from a form submission, redirect to login page
    if request.method == 'GET' or 'hold_id' not in request.session:
        return redirect('/login')

    # If there's already a logged in user, redirect to home page 
    if 'logged_user' in request.session:
        return redirect('/home')
    else:
        # Retrieve the user that's successfully logged in
        user = User.objects.get(id = request.session['hold_id'])

        # Check that entered verification code matches the one Twilio sent out
        phone_number = user.phone_number
        verification_check = client.verify \
                           .services(os.environ['TWILIO_SERVICE_ID']) \
                           .verification_checks \
                           .create(to=phone_number, code=request.POST['verification_code'].strip())
        
        # If code is incorrect, redirect them to verification page w/ error message
        if verification_check.status != 'approved':
            messages.error(request, "Incorrect verification code")
            return redirect('/verification')
        
        # Otherwise, stop holding user id, hold that id in logged_user instead
        # If it's their first time ever logging in, direct them to the edit profile page
        # Otherwise, redirect them to the home page
        else:
            del request.session['hold_id']
            request.session['logged_user'] = user.id
            if 'first' in request.session:
                return redirect('/edit_profile')
            else:
                return redirect('/home')

# Render the login page
# If already a logged in user, redirect to home page
# If no logged user, but an id is being held, then redirect to verification page
def login(request):
    if 'logged_user' in request.session:
        return redirect('/home')
    if 'hold_id' in request.session:
        return redirect('/verification')
    else:
        return render(request, 'login.html')

# Process a user login
def process_login(request):
    # Perform appropriate precautionary redirects
    if request.method == 'GET':
        return redirect('/login')
    if 'logged_user' in request.session:
        return redirect('/home')
    else:
        # Validate submitted data using the appropriate validator for the User object in models.py
        errors = User.objects.login_validator(request.POST)

        # If there are errors, redirect them to login page with error messages
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

           # Find user based on unique phone number 
            user = User.objects.filter(phone_number = phone_number)[0]
            if not user:
                messages.error(request, "No user with this phone number")
                return redirect('/login')

            # If no password associated w/ user, encode their entered passcode and enter it into the database
            # Store in the session that this is their first time ever logging in
            if not user.password:
                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user.password = pw_hash
                request.session['first'] = "yes"
            user.save() 

            # Hold user's id in session to indicate successful login, but pending verification
            request.session['hold_id'] = user.id

            # Use Twilio to send 6-digit code to user's phone number
            verification = client.verify \
                     .services(os.environ['TWILIO_SERVICE_ID']) \
                     .verifications \
                     .create(to=phone_number, channel='sms')
            
            # Take user to verification page
            return redirect('/verification')          

# Render edit profile page with the context of the logged in user
def edit_profile(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    context = {
        'user': User.objects.get(id = request.session['logged_user'])
    }
    return render(request, 'edit_profile.html', context)

# Process user edits of their profile
def process_edit_profile(request):
    # Perform appropriate cautionary redirects
    if request.method == 'GET':
        return redirect('/edit_profile')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        # Validate submitted data using the appropriate validator for the User object in models.py
        # errors = User.objects.edit_profile_validator(request.POST)
        errors = {}

        # If there are errors, redirect them to edit profile page with error messages
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/edit_profile')
        else:
            # Get user object associated with logged in user
            user = User.objects.get(id = request.session['logged_user'])

            # Since we are making it possible that users can leave certain fields blank,
            # We need if statements to check if they have entered something for each field

            # if request.POST['year']:
            #     user.year = request.POST['year'].strip()
            # else:
            #     user.year = ""

            # # If there is department data, clean it before assigning it
            # if request.POST['department1']:
            #     department1 = ""
            #     department1_raw = request.POST['department1'].strip().split(' ')
            #     for i in range(len(department1_raw)):
            #         department1 += department1_raw[i][0].upper() + department1_raw[i][1:].lower()
            #         if i != len(department1_raw) - 1:
            #             department1 += " "
            #     user.department1 = department1

            # if request.POST['department2']:
            #     department2 = ""
            #     department2_raw = request.POST['department2'].strip().split(' ')
            #     for i in range(len(department2_raw)):
            #         department2 += department2_raw[i][0].upper() + department2_raw[i][1:].lower()
            #         if i != len(department2_raw) - 1:
            #             department2 += " "
            #     user.department2 = department2

            # # If user entered a department2 but not a department1, then make department1 = department2 and clear department2
            # if request.POST['department2'] and not request.POST['department1']:
            #     user.department1 = user.department2
            #     user.department2 = ""

            # If there is title data, clean it before assigning it
            if 'title' in request.POST and len(request.POST['title'].strip()) > 0:
                title = request.POST['title'].strip()
                title = title.title()
                user.title = title
            
            # If there is profile picture data, assign it to logged user
            if len(request.FILES) > 0:
                user = User.objects.get(id = request.session['logged_user'])
                user.profile_picture = request.FILES.getlist('profile_picture')[0]
            
            # Save changes to user object
            user.save()

            # If it was their first time logging in, delete session variable indicating that and take them to homepage
            # Otherwise, take them back to their profile page
            if 'first' in request.session:
                del request.session['first']
                return redirect('/home')
            return redirect('/my_profile')

# Process user logout by removing all session variables and redirecting to landing page
def logout(request):
    if 'logged_user' or 'hold_id' in request.session:
        for key in list(request.session.keys()):
            del request.session[key]
    return redirect('/')

# Render page for reviewing applications from generic review link
def review_redir(request):
    # Prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session:
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('/home')

    # B/c this comes from the generic link, get the latest unapproved application,
    # Then redirect to the review page for that specific application
    if User.objects.filter(status = False).all().count() > 0:
        min = User.objects.filter(status = False).all().first().id
        return redirect('/review/{}'.format(min))

    # If no applications left to review, render review page w/ message
    else:
        context = {
            'empty': True
        }
        return render(request, 'review.html', context)

# Render review page for specific application
def review(request, num):
    # Prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session: 
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('/home')
        
    # If user id doesn't exist or already been approved, redirect to generic review link
    # so that the latest application can be displayed
    if User.objects.filter(id = num).all().count() < 1:
        return redirect('/review')
    
    user = User.objects.get(id = num)
    if user.status == True:
        return redirect('/review')
    
    # Provide to context the desired user, as well as the previous and next unapproved user according to id order
    context = {
        'applicant': user, 
        'total_current_users': User.objects.filter(status = True).all().count(),
        'total_unapproved_applications': User.objects.filter(status = False).all().count(),
    }
    greater_than = User.objects.filter(status = False, id__gt = user.id).all()
    less_than = User.objects.filter(status = False, id__lt = user.id).all()
    if greater_than.count() > 0:
        context['next_user'] = greater_than.first()
    if less_than.count() > 0:
        context['previous_user'] = less_than.last()
    return render(request, 'review.html', context)

# Process application approval
def process_approve(request):
    if request.method == 'GET':
        return redirect('/review')
    
    # Get user object from hidden POST response of id
    # Change user status to true (meaning approved) and save user object
    # Fire off welcome email to user email
    id = request.POST['id']
    user = User.objects.get(id = id)
    subject = 'Your Application to Join The Rise'
    message = f'Hi {user.first_name},\n\nThank you for applying to join The Rise (previously Humanely Digital). Your application has been reviewed and accepted for our beta testing period!\n\nThe Rise is a platform where audio-based news is produced for communities by communities. Our mission is to design an online environment where information is more democratized, truthful, valuable and diverse, in order to instigate real world impact. Therefore, we do not uphold toxic behaviour or low-quality entertainment based content.\n\nWe are so excited to welcome you into our community as we continue to build a new way to engage with high quality information and people online.  To complete your signup process, head over to https://therise.online/login. Make sure you access the platform via the Chrome browser, the Safari version is coming soon. Once your account has been created, please refer to ‘The Rise’ onboarding space.\n\nEscape the attention economy and discuss what matters.\n\nWarmly,\nThe Rise Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    send_mail(subject, message, 'The Rise (previously Humanely Digital) <team@therise.online>', recipient_list)
    user.status = True
    user.save()
    return redirect('/review')

# Render profile page
def profile(request, num):
    if 'logged_user' not in request.session:
        return redirect('/login')
    
    # If no user exists with provided id, redirect
    if User.objects.filter(id = num).all().count() < 1:
        return redirect('/home')
    # If provided id is id of logged in user, redirect to my profile page
    if num == request.session['logged_user']:
        return redirect('/my_profile')
    context = {
        'logged_user': User.objects.get(id = request.session['logged_user']),
        'user': User.objects.get(id = num)
    }
    return render(request, 'profile.html', context)

# Render profile of logged_user (essentially unnecessary but kept to have 'my_profile' url differentiator)
def my_profile(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    context = {
        'user': User.objects.get(id = request.session['logged_user'])
    }
    return render(request, 'profile.html', context)

# Render page to add new spaces
def add_space(request):
    # Prevent access to those not logged in or don't have permission
    if 'logged_user' not in request.session: 
        return redirect('/login')
    if User.objects.get(id = request.session['logged_user']).permissions < 1:
        return redirect('/home')
    return render(request, 'add_space.html')

# Process a new space being added
def process_add_space(request):
    if request.method == "GET":
        return redirect('/spaces')
    # Clean submitted data, then create a new Space object
    name = request.POST['name'].strip().title()
    Space.objects.create(name = name, network = Network.objects.get(id = 1))
    return redirect('/home')

# Process a new discussion being posted
def process_discussion_post (request):
    # Perform appropriate cautionary redirects
    if request.method == 'GET':
        return redirect('/home')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        # Validate submitted data using the appropriate validator for the Discussion object in models.py
        errors = Discussion.objects.post_validator(request.POST, request.FILES)

         # If there are errors, re-render the discussion form with error messages
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return render(request, 'partials/post_discussion.html')
        else:
            # Clean data
            title = request.POST['title'].strip()
            participant_cap = request.POST['participant_cap']
            link = request.POST['link'].strip()
            user = User.objects.get(id = request.session['logged_user'])
            duration = request.POST['duration'].strip()

            # Get title of link to display rather than raw url, if unable, then display raw_url
            # Saved in database to reduce conversion time
            try:
                link_html = urlopen(link).read()
                soup = BeautifulSoup(link_html)
                link_title = soup.title.string
            except:
                link_title = link
            # Create Discussion w/ cleaned data in currently selected space
            space = Space.objects.get(id = request.session['current_space'])
            Discussion.objects.create(title = title, participant_cap =  participant_cap, link = link, link_title = link_title, audio = request.FILES.getlist('audio_recording')[0], poster = user, space = space, duration = duration)
            context = {
                'discussions': space.discussion_posts.all().order_by('-created_at')
            }
            return render(request, 'partials/post_discussion.html', context)

# Render discussions of selected space dynamically via AJAX
def space(request, network, space):
    if 'logged_user' not in request.session:
        return redirect('/home')

    # Store clicked on space as current space in session variable
    request.session['current_space'] = space

    # Pass to discussion posts section the current space and its discussions
    context = {
        'current_space': Space.objects.get(id = request.session['current_space'])
    }
    context['discussions'] = context['current_space'].discussion_posts.all().order_by('-created_at')

    # Overwrite currently selected discussion with most recent Discussion in selected space
    if context['discussions'].count() > 0:
        request.session['current_discussion'] = context['discussions'].first().id
        request.session['current_discussion_index'] = 0
    else:
        request.session['current_discussion'] = None
        request.session['current_discussion_index'] = 0

    print(context['discussions'])
    return render(request, 'partials/discussion_posts.html', context)

# Render corresponding discussion banner for selected space
def load_discussion_banner(request):
    if 'logged_user' not in request.session:
        return redirect('/home')
    context = {
        'current_space': Space.objects.get(id = request.session['current_space']),
        'favorite_spaces': User.objects.get(id = request.session['logged_user']).favorite_spaces.all(),
    }
    return render(request, 'partials/discussion_banner.html', context)

# Render corresponding response banner for selected discussion
def load_response_banner(request):
    if 'logged_user' not in request.session:
        return redirect('/home')
    space = Space.objects.get(id = request.session['current_space'])
    context = {
        'current_discussion': Discussion.objects.get(id = request.session['current_discussion']),
        'current_discussion_index': request.session['current_discussion_index'],
    }
    context['discussions'] = space.discussion_posts.all().order_by('-created_at')
    return render(request, 'partials/response_banner.html', context)

# Process a new response post
def process_response_post(request):
    # Perform appropriate cautionary redirects
    if request.method == 'GET':
        return redirect('/home')
    if 'logged_user' not in request.session:
        return redirect('/login')
    else:
        # Validate submitted data using the appropriate validator for the Response object in models.py
        errors = Response.objects.post_validator(request.POST, request.FILES)

        # If there are errors, re-render the response form with error messages
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return render(request, 'partials/post_response.html')
        else:
            # Since link is optional for responses, only perform checks for it if present
            # Checks are similar to those performed for Discussion
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

            # Create Response w/ cleaned data within currently selected Discussion
            user = User.objects.get(id = request.session['logged_user'])
            discussion = Discussion.objects.get(id = request.session['current_discussion'])
            if discussion.participants.all().count() == discussion.participant_cap and user not in discussion.participants.all():
                messages.error(request, "This discussion is at its participant cap!")
                return render(request, 'partials/post_response.html')
            duration = request.POST['duration'].strip()
            Response.objects.create(link = link, link_title = link_title, audio = request.FILES.getlist('audio_recording')[0], poster = user, discussion = discussion, duration = duration)
            if user not in discussion.participants.all():
                discussion.participants.add(user)
                discussion.participant_count+=1
                discussion.save()
            return render(request, 'partials/post_response.html')

# Render responses associated w/ currently selected discussion dyanmically via AJAX
def load_responses(request, num, num2):
    if 'logged_user' not in request.session:
        return redirect('/login')
    discussion = Discussion.objects.get(id = num)
    space = discussion.space
    request.session['current_discussion'] = num
    request.session['current_discussion_index'] = num2
    print(request.session['current_discussion'], request.session['current_discussion_index'])
    context = {
        'current_discussion': discussion,
        'current_discussion_index': request.session['current_discussion_index'],
        'discussions': space.discussion_posts.all().order_by('-created_at')
    }
    return render(request, 'partials/response_posts_block.html', context)

# Process toggling favorite button on space and render updated spaces dynamically via AJAX
def process_favorite_space(request, num):
    
    if 'logged_user' not in request.session:
        return redirect('/login')
    space = Space.objects.get(id = num)
    user = User.objects.get(id = request.session['logged_user'])
    
    if space in user.favorite_spaces.all():
        user.favorite_spaces.remove(space)
    else:
        user.favorite_spaces.add(space)
    user.save()
    context = {
        'spaces': Space.objects.all(),
        'favorite_spaces': user.favorite_spaces.all()
    }
    return render(request, 'partials/spaces_block.html', context)

# Render discussions sorted dynamically based on which option user selected (top, recent, saved) via AJAX
def discussion_button_pressed(request, num, lorem):
    if 'logged_user' not in request.session:
        return redirect('/login')
    context = {}
    current_space = Space.objects.get(id = request.session['current_space'])
    user = User.objects.get(id = request.session['logged_user'])
    if lorem == "top":
        context['discussions'] = current_space.discussion_posts.all().annotate(q_count = Count('saved_users')).order_by('-q_count')
    elif lorem == "saved":
        context['discussions'] = user.saved_discussions.all().filter(space = current_space).all().order_by('-created_at')
    else:
        context['discussions'] = current_space.discussion_posts.all().order_by('-created_at')
    context['logged_user'] = user
    return render(request, 'partials/discussion_posts.html', context)

# Process toggling saved button on discussion and render updated discussion posts dynamically via AJAX
def process_save_discussion(request, num):
    if 'logged_user' not in request.session:
        return redirect('/login')
    discussion = Discussion.objects.get(id = num)
    user = User.objects.get(id = request.session['logged_user'])
    space = Space.objects.get(id = request.session['current_space'])

    if discussion in user.saved_discussions.all():
        user.saved_discussions.remove(discussion)
    else:
        user.saved_discussions.add(discussion)
    user.save()
    context = {
        'logged_user': user,
        'discussions': space.discussion_posts.all().order_by('-created_at'),
    }
    return render(request, 'partials/discussion_posts.html', context)


def process_space_search(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    query = request.POST['space_query'].strip().title()

    if query == "":
        user = User.objects.get(id = request.session['logged_user'])
        context = {
            'spaces': Space.objects.all(),
            'favorite_spaces': user.favorite_spaces.all()
        }
        return render(request, 'partials/spaces_block.html', context)
    else:
        context = {
        'resulting_spaces': Space.objects.filter(Q(name__startswith = query)| Q(name__icontains = query)) .all(),
        }
        return render(request, 'partials/space_search_result.html', context)

def display_spaces(request):
    if 'logged_user' not in request.session:
        return redirect('/login')
    user = User.objects.get(id = request.session['logged_user'])
    context = {
        'spaces': Space.objects.all(),
        'favorite_spaces': user.favorite_spaces.all()
    }
    return render(request, 'partials/spaces_block.html', context)
    




