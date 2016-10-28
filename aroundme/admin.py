from django.contrib import admin
from .models import Member, Anniversary, PersonalEvent, Photo

admin.site.register(Member)
admin.site.register(Anniversary)
admin.site.register(PersonalEvent)
admin.site.register(Photo)