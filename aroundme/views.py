from django.shortcuts import render, redirect
from django.template import RequestContext
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.exceptions import ObjectDoesNotExist
import json
from itertools import chain

from .my_exceptions import EmptyQuerySetException
from .models import Member, Friend, PersonalEvent, Anniversary
from .forms import SignupForm


# View method of member signup

def view_member_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password_input'],
                email=form.cleaned_data['email_id']
            )
            return redirect(view_event_list)
    else:  # HTTP GET case
        form = SignupForm()

    content = RequestContext(request, {
        'form': form
    })

    return render(request, 'registration/signup.html', content)


# View methods of main page (checking User login / out)

@login_required
def view_main_page(request):
    # 추가 구현!!!

    return redirect(view_event_list)


# View methods of schedule list (right side in main page)

@login_required
def view_event_list(request):
    p_events = PersonalEvent.objects.filter(user=request.user)
    a_events = Anniversary.objects.filter(user=request.user)

    event_list = sorted(
        chain(p_events, a_events),
        key=lambda instance: instance.updated_at
    )

    event_list_set = []

    #print("Debug : event_list length : ", len(event_list))
    print(event_list)

    try:
        if not event_list and (
                    (isinstance(p_events, EmptyQuerySet) != True) or (isinstance(a_events, EmptyQuerySet) != True)):
            raise EmptyQuerySetException()
    except EmptyQuerySetException as e:
        print(e)
    else:
        for event in event_list:
            if isinstance(event, PersonalEvent):
                d_start = event.datetime_start.strftime('%Y.%m.%d %H:%M')
                d_end = event.datetime_finish.strftime('%Y.%m.%d %H:%M')
                event_dict = {
                    'type' : 'p_event', 'id' : event.id, 'user' : event.user, 'description' : event.description,
                    'd_start' : d_start, 'd_end' : d_end, 'place' : event.place
                }
                event_list_set.append(event_dict)
            else:
                event_dict = {
                    'type' : 'anniversary', 'id' : event.id, 'user' : event.user, 'description' : event.description,
                    'd_start' : event.date, 'd_end' : event.date, 'place' : event.place
                }
                event_list_set.append(event_dict)


    context = RequestContext(request, {
        'event_list_set': event_list_set,
    })

    return render(request, 'AM_schedule.html', context)


# If it's from clicking 'save' button on 'add schedule' modal

@login_required
@csrf_exempt
def event_save_schedule(request):

    if request.method == 'POST':
        p_event = _create_personal_event(request)
        response_data = {}

        response_data['result'] = 'success!'
        response_data['description'] = p_event.description
        response_data['place'] = p_event.place
        response_data['time-start'] = p_event.datetime_start
        response_data['time-finish'] = p_event.datetime_finish

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see" : "nothing"}),
            content_type="application/json"
        )
#    return redirect(view_event_list)


def _create_personal_event(request):
    p_event = PersonalEvent()

    p_event.user = request.user
    p_event.description = request.POST.get('description')
    p_event.place = request.POST.get('place')
    p_event.datetime_start = request.POST.get('time_start')
    p_event.datetime_finish = request.POST.get('time_finish')

    print(request.POST.get('description'))
    print(request.POST.get('place'))
    print(request.POST.get('time-start'))
    print(request.POST.get('time-finish'))

    p_event.save()

    return p_event

@login_required
def event_delete_schedule(request):
    print('in views:event_delete_schedule')

    if request.method == 'POST':
        try:
            delete_type = request.POST.get('type')
            delete_id = request.POST.get('id')
            print('in if POST %s %s' % (delete_type, delete_id))

            if delete_type == 'p_event':
                try:
                    delete_p_event = PersonalEvent.objects.filter(id=delete_id)
                    delete_p_event.delete()
                except ObjectDoesNotExist:
                    print('delete case personal event')
                    print('ObjectDoesNotExist : id %d does not exist' % delete_id)
            elif delete_type == 'anniversary':
                try:
                    delete_a_event = Anniversary.objects.filter(id=delete_id)
                    delete_a_event.delete()
                except ObjectDoesNotExist:
                    print('delete case anniversary')
                    print('ObjectDoesNotExist : id %d does not exist' % delete_id)
            else:
                print('delete schedule : event type not matching case (should not happen)')
        except ObjectDoesNotExist:
            print('delete case type/id not exist')
            print('type : %s, id : %s' % (delete_type, delete_id))
    else:
        print('weird...GET case of event_delete_schedule')

    return redirect(view_event_list)