from django.contrib import admin
from .models import Member, Anniversary, PersonalEvent

admin.site.register(Member)
admin.site.register(Anniversary)
admin.site.register(PersonalEvent)