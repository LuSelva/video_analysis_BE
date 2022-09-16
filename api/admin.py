from django.contrib import admin
from .models import User, Video, Segment

admin.site.register(User)
admin.site.register(Video)
admin.site.register(Segment)