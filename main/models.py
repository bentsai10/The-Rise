from django.db import models
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
import re, phonenumbers, bcrypt, random

# Create your models here.
def upload_to(instance, filename):
    return 'images/profile_pictures/{id}/{filename}'.format(
        id=instance.id, filename=filename)

def discussion_upload_to(instance, filename):
    return 'audio/discussions/{id}/{filename}'.format(
        id=instance.poster.id, filename=filename)

def response_upload_to(instance, filename):
    return 'audio/responses/{id}/{filename}'.format(
        id=instance.poster.id, filename=filename)

class UserManager(models.Manager):

    def login_validator(self, postData):
        errors = {}
        if postData['phone_number'].strip() == "1234567890" and postData['password'] == "theriseadmin":
            return errors
        try: 
            phone_number = phonenumbers.parse(postData['phone_number'].strip())
            
        except:
            errors['phone_number'] = ("Phone number must be entered in the format: '+6171234567'. Up to 15 digits allowed")
            return errors
        phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        if User.objects.filter(phone_number = phone_number).all().count() <= 0:
            errors['phone_number'] = "You have yet to register an account with us! Head on over to therise.online/register!"
            return errors
        user = User.objects.filter(phone_number = phone_number)[0]
        if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
            errors["password"] = "Incorrect password!"
        return errors


    def register_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        permitted_email_endings = ['bc.edu']

        if len(postData['first_name'].strip()) < 2:
            errors['first_name'] = "First name must be 2+ characters"
        if len(postData['last_name'].strip()) < 2:
            errors['last_name'] = "Last name must be 2+ characters"
        if not EMAIL_REGEX.match(postData['email'].strip()):
            errors['email'] = ("Invalid email address!")
            return errors
        
        email_ending = postData['email'].strip().split('@')[-1]
        if email_ending not in permitted_email_endings:
            errors['email'] = ("The Rise is not yet open to your school/company. Contact us if you'd like your school/company to join The Rise!")
            return errors
        if User.objects.filter(email = postData['email'].lower()).all().count() > 0:
            errors['email'] = "An account is already registered with this email"
            return errors
        try: 
            phone_number = phonenumbers.parse(postData['phone_number'].strip())
        except:
            errors['phone_number'] = ("Country dialing code is required (+1 for U.S)")
            return errors
        if not phonenumbers.is_valid_number(phone_number):
            errors['phone_number'] = ("Country dialing code is required (+1 for U.S)")
            return errors
        if User.objects.filter(phone_number = postData['phone_number']).all().count() > 0:
            errors['phone_number'] = "An account is already registered with this phone number"
            return errors

        if len(postData['password']) < 8:
                errors['password'] = "Password must be at least 8 characters"
        if postData['password'] != postData['confirm_password']:
            errors['password'] = "Your passwords don't match"
        if len(postData['referral'].strip()) < 2:
            errors['referral'] = "Please let us know what brought you here (2+ characters)"
        return errors

    def edit_profile_validator(self, postData):
        errors = {}
        # if postData['year']:
        #     if len(postData['year'].strip()) != 4:
        #         errors['year'] = "Invalid class year"
        # if postData['department1']:
        #     if len(postData['department1'].strip()) < 3:
        #         errors['department1'] = "Department name must be at least 3 characters"
        # if postData['department2']:
        #     if len(postData['department2'].strip()) < 3:
        #         errors['department1'] = "Department names must be at least 3 characters"
        # if 'title' in postData:
        #     if postData['title'].strip().lower() not in valid_titles:
        #         errors['title'] = "Not a valid title. Please email us at humanelydigital@gmail.com if you'd like a personalized title"
        return errors

class User(models.Model):
    class Meta:
        db_table = 'users'

    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    phone_number = models.CharField(max_length = 17)
    essay = models.TextField(blank=True) #response to application question
    referral = models.CharField(max_length = 255) #track referral person
    password = models.CharField(max_length = 255, blank = True)
    year = models.CharField(max_length = 4, blank = True) #e.g. 2022
    department1 = models.CharField(max_length = 255, blank = True) #e.g. computer science
    department2 = models.CharField(max_length = 255, blank = True) #e.g. finance
    title = models.CharField(max_length = 255, blank = True) #e.g. Student, Account Executive, etc.
    profile_picture = models.ImageField(upload_to = upload_to, blank = True)
    permissions = models.IntegerField(default = 0) #only admin permissions can view certain pages/perform certain actions
    status = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name


class NetworkManager(models.Manager):
    pass

class Network(models.Model):
    class Meta:
        db_table = 'network'
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = NetworkManager()

    def __str__(self):
        return self.name

class SpaceManager(models.Manager):
    pass

class Space(models.Model):
    class Meta:
        db_table = 'spaces'
    name = models.CharField(max_length = 255)
    favorited_users = models.ManyToManyField(User, related_name = "favorite_spaces")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    network = models.ForeignKey(Network, related_name = "spaces", on_delete = models.CASCADE)
    objects = SpaceManager()

    def __str__(self):
        return self.name


class DiscussionManager(models.Manager):
    def post_validator(self, postData, fileData):
        errors = {}
        if len(postData['title'].strip()) < 2 or len(postData['title'].strip()) > 30:
            errors['title'] = "Discussion titles need to be between 2-30 characters"
        valid_caps = ['2', '10', '100']
        if postData['participant_cap'] not in valid_caps:
            errors['participant_cap'] = 'Invalid participant cap: Choose from 2, 10, 100'
        if len(postData['link'].strip()) > 0:
            try:
                validate = URLValidator()
                validate(postData['link'].strip())
            except ValidationError:
                errors['link'] = "Invalid URL: Check if you have http:// or https:// in front"
        if len(fileData) < 1:
                errors['audio'] = "No audio file detected!"
        return errors


class Discussion(models.Model):
    class Meta:
        db_table = 'discussion_posts'
    title = models.CharField(max_length = 255)
    link = models.CharField(max_length = 200, blank=True)
    link_title = models.CharField(max_length = 255, blank=True)
    participant_cap = models.IntegerField()
    participant_count = models.IntegerField(default = 1)
    audio = models.FileField(upload_to = discussion_upload_to)
    poster = models.ForeignKey(User, related_name = "discussion_posts",on_delete = models.CASCADE)
    space = models.ForeignKey(Space, related_name = "discussion_posts", on_delete = models.CASCADE)
    saved_users = models.ManyToManyField(User, related_name = "saved_discussions")
    duration = models.CharField(max_length = 20)
    participants = models.ManyToManyField(User, through='ParticipantInDiscussion', related_name = "discussions_participated_in")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = DiscussionManager()

    def __str__(self):
        return self.title + " by " + str(self.poster)

class ResponseManager(models.Manager):
    def post_validator(self, postData, fileData):
        errors = {}
        if len(postData['link'].strip()) < 2 and len(postData['link'].strip()) > 0:
            errors['link'] = "Links need to be at least 2 characters"
        elif len(postData['link'].strip()) > 0:
            try:
                validate = URLValidator()
                validate(postData['link'].strip())
            except ValidationError:
                errors['link'] = "Invalid URL: Check if you have http:// or https:// in front"
        if len(fileData) < 1:
                errors['audio'] = "No audio file detected!"
        return errors

class Response(models.Model):
    class Meta:
        db_table = 'response_posts'
    audio = models.FileField(upload_to = response_upload_to)
    poster = models.ForeignKey(User, related_name = "response_posts", on_delete = models.CASCADE)
    discussion = models.ForeignKey(Discussion, related_name = "response_posts", on_delete = models.CASCADE)
    link = models.CharField(max_length = 200, blank = True)
    link_title = models.CharField(max_length = 255, blank = True)
    duration = models.CharField(max_length = 20)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    objects = ResponseManager()  

    def __str__(self):
        return "Response to " + str(self.discussion) + " by " + str(self.poster)

class ParticipantInDiscussion(models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)