from django.db import models
from django.conf import settings


# Model related to user / members

class Member(models.Model) :
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=30)
    birthday = models.DateField(null=True, blank=True)
#    photo =
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.name


class Friend(models.Model) :
    name = models.CharField(max_length=30)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




# Models related to Events

class EventBase(models.Model) :
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
#    opponent = models.ForeignKey('Member', on_delete = models.CASCADE, related_name='%(class)s_member_sub')
    description = models.TextField(null=True, blank=True)
    place = models.TextField(max_length=100, null=True, blank=True)
#   photo =
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        abstract = True


class Anniversary(EventBase) :
    date = models.DateField()


class PersonalEvent(EventBase) :
    datetime_start = models.DateTimeField()
    datetime_finish = models.DateTimeField()



# Photo Model

