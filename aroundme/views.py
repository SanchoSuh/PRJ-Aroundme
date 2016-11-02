from django.shortcuts import render, redirect
from django.template import RequestContext
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import json
from itertools import chain

from .my_exceptions import EmptyQuerySetException
from .models import Member, Friend, PersonalEvent, Anniversary, Photo
from .forms import SignupForm


# View method of member signup

def view_member_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            # Create an User
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password_input'],
                    email=form.cleaned_data['email_id']
                )
            except ValueError:
                print('value error while creating user')

            # and create a member and map with the user
            # todo: membername unique validation
            try:
                member = Member()
                member.user = user
                member.name = user.username
                member.thumbnail = _create_default_thumbnail(user, user.username)
                member.save()

                user.set_password(form.cleaned_data['password_input'])
                # login to the new user
                user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password_input'],
                )
                auth_login(request, user)

            except ValidationError:
                print('validation error : %s %s' % member.user, member.name)
                print('alert')

            return redirect(view_event_list)
    else:  # HTTP GET case
        form = SignupForm()

    content = RequestContext(request, {
        'form': form
    })

    return render(request, 'registration/signup.html', content)

# Create a default thumbnail image and link to member
def _create_default_thumbnail(user, username):
    d_photo = Photo()

    d_photo.user = user
    d_photo.description = username
    d_photo.save()

    return d_photo


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
    member = Member.objects.get(user=request.user)

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
                d_start = event.date_start.strftime('%Y.%m.%d')
                d_end = event.date_finish.strftime('%Y.%m.%d')
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


    print('member data validation check : name : %s, thumbnail: %s' % (member.name, member.thumbnail))

    context = RequestContext(request, {
        'event_list_set': event_list_set,
        'member' : member,
    })

    return render(request, 'AM_schedule.html', context)


# If it's from clicking 'save' button on 'add schedule' modal

@login_required
@csrf_exempt
def event_save_schedule(request):
    data_id = request.POST.get('id')
    data_type = request.POST.get('type')

    response_data = {}

    if request.method == 'POST':
        if data_id:
            print('views:event_save_schedule | in case of editing a pre-saved schedule')
            try:
                if data_type == 'Anniversary':
                    print('[debug] anniversary')
                    get_anniversary = Anniversary.objects.get(id=data_id)
                    get_anniversary.description = request.POST.get('description')
                    get_anniversary.place = request.POST.get('place')
                    get_anniversary.date = request.POST.get('time_start')
                    # TODO: Anniversary shouldn't have start or finish
                    get_anniversary.save()

                elif data_type == 'p_event':
                    print('[debug] personal event')
                    get_pevent = PersonalEvent.objects.get(id=data_id)
                    get_pevent.description = request.POST.get('description')
                    get_pevent.place = request.POST.get('place')
                    get_pevent.date_start = request.POST.get('time_start')
                    get_pevent.date_finish = request.POST.get('time_finish')
                    get_pevent.save()

            except ObjectDoesNotExist:
                print('[error] ObjectDoesNotExist - getting event from models by id')

            else:
                response_data['result'] = 'success'

        else:
            print('views:event_save_schedule | in case of creating new schedule')
            p_event = _create_personal_event(request)

            response_data['result'] = 'success'
            response_data['description'] = p_event.description
            response_data['place'] = p_event.place
            response_data['time-start'] = p_event.date_start
            response_data['time-finish'] = p_event.date_finish

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
    p_event.date_start = request.POST.get('time_start')
    p_event.date_finish = request.POST.get('time_finish')

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
        print('views:event_delete_schedule | NOT POST of HttpRequest')

    return redirect(view_event_list)

@login_required
def event_get_schedule(request) :
    print('in views:event_edit_schedule')

    response_data = {}

    if request.method == 'POST':
        try:
            edit_id = request.POST.get('id')
            edit_type = request.POST.get('type')

            if edit_type == 'p_event':
                try:
                    edit_p_event = PersonalEvent.objects.get(id=edit_id)
                    response_data['result'] = 'success'
                    response_data['id'] = edit_id
                    response_data['type'] = edit_type
                    response_data['description'] = edit_p_event.description
                    response_data['place'] = edit_p_event.place
                    response_data['date_start'] = edit_p_event.date_start
                    response_data['date_finish'] = edit_p_event.date_finish

                except ObjectDoesNotExist:
                    print('views:event_edit_schedule | PersonalEvent id %d not exit' % edit_id)

            elif edit_type == 'anniversary':
                try:
                    edit_a_event = Anniversary.objects.get(id=edit_id)
                    response_data['result'] = 'success'
                    response_data['id'] = edit_id
                    response_data['type'] = edit_type
                    response_data['description'] = edit_a_event.description
                    response_data['place'] = edit_a_event.place
                    response_data['date_start'] = edit_a_event.date
                    response_data['date_finish'] = edit_a_event.date

                except ObjectDoesNotExist:
                    print('views:event_edit_schedule | PersonalEvent id %d not exit' % edit_id)

            else:
                print('views:event_edit_schedule | Type error. Nor p_event neither Anniversary')
                response_data['result'] = 'fail'

        except ObjectDoesNotExist:
            print('views:event_edit_schedule | object not exist')
            response_data['result'] = 'fail'
    else:
        print('views:event_edit_schedule | NOT POST of HttpRequest')
        response_data['result'] = 'fail'

    return HttpResponse(
                json.dumps(response_data, default=date_handler),
                content_type="application/json"
            )


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError