from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Network)
admin.site.register(Space)
admin.site.register(Discussion)
admin.site.register(Response)