from django.db import models
from django.core.validators import RegexValidator
import re, phonenumbers, bcrypt, random

# Create your models here.
def upload_to(instance, filename):
    return 'images/profile_pictures/{id}/{filename}'.format(
        id=instance.id, filename=filename)

class UserManager(models.Manager):
    def verification_validator(self, postData, userID):
        errors = {}
        user = User.objects.get(id = userID)
        if postData['verification_code'] != user.verification_code:
            errors['verification_code'] = "Incorrect verification code"
        return errors

    def login_validator(self, postData):
        errors = {}
        try: 
            phone_number = phonenumbers.parse(postData['phone_number'].strip())
            
        except:
            errors['phone_number'] = ("Phone number must be entered in the format: '+6171234567'. Up to 15 digits allowed")
            return errors
        phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        if User.objects.filter(phone_number = phone_number).all().count() <= 0:
            errors['phone_number'] = "You have yet to apply for access to our platform. Head on over to humanelydigital.com/apply!"
            return errors
        user = User.objects.filter(phone_number = phone_number)[0]
        if user and user.status == False:
            errors['phone_number'] = "Please be patient while we continue to review applications to our platform. Feel free to contact us at humanelydigital@gmail.com"
            return errors
        if not user.password:
            if postData['password'] != postData['confirm_password']:
                errors['password'] = "Your passwords do not match!"
            if len(postData['password']) < 8:
                errors['password'] = "Password must be at least 8 characters"
        if user.password:
            print(bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()).decode())
            if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                errors["password"] = "Incorrect password!"
        return errors

    def register_validator(self, postData):
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

        if len(postData['first_name'].strip()) < 2:
            errors['first_name'] = "First name must be 2+ characters"
        if len(postData['last_name'].strips()) < 2:
            errors['last_name'] = "Last name must be 2+ characters"
        if not EMAIL_REGEX.match(postData['email'].strip()):
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
        if len(postData['essay'].strip()) < 15:
            errors['essay'] = "Please be thoughtful in your response (15+ characters)"
        if len(postData['referral'].strip()) < 2:
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
    verification_code = models.CharField(max_length = 6, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    def save(self, *args, **kwargs):
        num_list = [x for x in range(10)]
        code = []
        for i in range (6):
            num = random.choice(num_list)
            code.append(num)
        code_str = "".join(str(n) for n in code)
        self.verification_code = code_str
        super().save(*args, **kwargs)
  