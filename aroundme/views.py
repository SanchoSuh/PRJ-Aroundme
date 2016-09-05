from django.shortcuts import render, redirect
from .models import Member
from .member_views import *

def main_view(request) :
    members = Member.objects.order_by('-updated_at')
    content = {
        'member_list' : members,
    }

    return render(request, 'AM_schedule.html', content)