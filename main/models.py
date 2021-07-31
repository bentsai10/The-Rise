from django.db import models
from django.core.validators import RegexValidator
import re, phonenumbers

from . import secrets

# Create your models here.
def upload_to(instance, filename):
    return 'images/profile_pictures/{id}/{filename}'.format(
        id=instance.id, filename=filename)

class UserManager(models.Manager):
    def registervalidator(self, postData):
        errors = {}
        permitted_email_endings = ['bc.edu', ]
        email_ending = postData['email'].split('@')[-1]

        if email_ending not in permitted_email_endings:
            errors['email'] = ("Please register with your school/work email! Check our platform availability for your school/company at humanelydigital.com")
            return errors
        return errors
    def apply_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        if len(postData['first_name']) < 2:
            errors['first_name'] = "First name must be 2+ characters"
        if len(postData['last_name']) < 2:
            errors['last_name'] = "Last name must be 2+ characters"
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = ("Invalid email address!")
            return errors
        if User.objects.filter(email = postData['email'].lower()).all().count() > 0:
            errors['email'] = "An application has already been submitted with this email"
            return errors
        try: 
            phone_number = phonenumbers.parse(postData['phone_number'].strip())
        except:
            errors['phone_number'] = ("Phone number must be entered in the format: '+6171234567'. Up to 15 digits allowed")
            return errors
        if not phonenumbers.is_valid_number(phone_number):
            errors['phone_number'] = ("Number invalid. Phone number must be entered in the format: '+6171234567'. Up to 15 digits allowed")
            return errors
        if User.objects.filter(phone_number = postData['phone_number']).all().count() > 0:
            errors['phone_number'] = "An application has already been submitted with this phone number"
            return errors
        if len(postData['essay']) < 15:
            errors['essay'] = "Please be thoughtful in your response (15+ characters)"
        if len(postData['referral']) < 2:
            errors['referral'] = "Please let us know what brought you here (2+ characters)"
        return errors

class User(models.Model):
    class Meta:
        db_table = 'users'
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    phone_number = models.CharField(max_length = 17)
    essay = models.TextField() #response to application question
    referral = models.CharField(max_length = 255) #track referral person
    password = models.CharField(max_length = 255, blank = True)
    year = models.CharField(max_length = 255, blank = True) #e.g. senior
    department1 = models.CharField(max_length = 255, blank = True) #e.g. computer science
    department2 = models.CharField(max_length = 255, blank = True) #e.g. finance
    title = models.CharField(max_length = 255, blank = True) #e.g. Student, Account Executive, etc.
    profile_picture = models.ImageField(upload_to = upload_to, blank = True)
    permissions = models.IntegerField(default = 0) #only admin permissions can view certain pages/perform certain actions
    status = models.BooleanField(default = False) #not accepted to begin with
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()
    