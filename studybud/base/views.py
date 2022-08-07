from ast import If
from multiprocessing import context;
from django.contrib import messages;
from unicodedata import name;
from django.db.models import Q;
from django.shortcuts import render, redirect;
from .models import Room, Topic, Message;
from .forms import RoomForm, UserForm;
from django.contrib.auth.models import User;
from django.contrib.auth import authenticate, login, logout;
from django.contrib.auth.decorators import login_required;
from django.http import HttpResponse;
from django.contrib.auth.forms import UserCreationForm;

# Create your views here.

def loginPage(req):
    page = 'login';
    if req.user.is_authenticated:
        return redirect('home');

    if req.method == 'POST':
        username = req.POST.get('username').lower();
        password = req.POST.get('password');

        try :
            user = User.objects.get(username=username);
        except:
            messages.error(req, 'User does not exist');

        user = authenticate(req, username=username, password=password);

        if user is not None:
            login(req, user);
            return redirect('home');
        else:
           messages.error(req, 'Username Or password does not exist');
        

    context = {'page': page};
    return render(req, 'base/login_register.html', context);



def logoutPage(req):
    logout(req);
    return redirect('home');



def registerPage(req):
    form = UserCreationForm();

    if req.method == 'POST':
        form = UserCreationForm(req.POST);
        if form.is_valid():
            user = form.save(commit=False);
            user.username = user.username.lower();
            user.save();
            login(req, user);
            return redirect('home');
        else:
            messages.error(req, 'An error occurred during registration');  

    context = {'form': form};
    return render(req, 'base/login_register.html', context);



def home(req):
    q = req.GET.get('q') if req.GET.get('q') != None else '';

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
        );

    room_count = rooms.count();
    topics = Topic.objects.all();

    room = Room.objects.all();
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q));
    # room_messages = Message.objects.all();

    # print(room);


    context = {
        'rooms': rooms, 
        'topics': topics,
        'room_count': room_count, 
        'room_messages': room_messages
        };

    return render(req, 'base/home.html', context);



def room(req, pk):
    room = Room.objects.get(id=pk);
    room_messages = room.message_set.all()
    participants = room.participants.all();

    if req.method == 'POST':
        message = Message.objects.create(
            user=req.user,
            room=room,
            body=req.POST.get('body'),
        );
        room.participants.add(req.user);
        return redirect('room', pk=room.id);

    context = {'room': room, 'room_messages': room_messages, 'participants': participants};    
    return render(req, 'base/room.html', context);


def userProfile(req, pk):
    user = User.objects.get(id=pk);
    room_messages = user.message_set.all();
    rooms = user.room_set.all();
    topics = Topic.objects.all();
    context = {
        'user': user, 
        'rooms': rooms, 
        'room_messages': room_messages,
        'topics': topics,
        };
    return render(req, 'base/profile.html', context);


@login_required(login_url='/login')
def createRoom(req):
    form = RoomForm();
    topics = Topic.objects.all();
    if req.method == 'POST':
        # print(req.POST);
        topic_name = req.POST.get('topic');
        topic, created = Topic.objects.get_or_create(name=topic_name);

        Room.objects.create(
            host=req.user,
            topic=topic,
            name=req.POST.get('name'),
            description=req.POST.get('description')
        );
        return redirect('home');
        # form = RoomForm(req.POST);
        # if form.is_valid():
        #     room = form.save(commit=False);
        #     room.host = req.user;
        #     room.save();

    context = {'form': form, 'topics': topics};
    return render(req, 'base/room_form.html', context);



@login_required(login_url='login')
def updateRoom(req, pk):
    room = Room.objects.get(id=pk);
    form = RoomForm(instance=room);
    topics = Topic.objects.all();
    if req.user != room.host:
        return HttpResponse('You are not allowed here!');

    if req.method == 'POST':
        topic_name = req.POST.get('topic');
        topic, created = Topic.objects.get_or_create(name=topic_name);
        room.name = req.POST.get('name');
        room.topic = topic;
        room.description = req.POST.get('description');
        room.save();

        return redirect('home');

    context = {
        'form': form, 
        'topics': topics, 
        'room': room
        };
    return render(req, 'base/room_form.html', context);


    
@login_required(login_url='/login')    
def deleteRoom(req, pk):
    room = Room.objects.get(id=pk);

    if req.user != room.host:
        return HttpResponse('You are not allowed here!');

    if req.method == 'POST':
        room.delete();
        return redirect('home');
    return render(req, 'base/delete.html', {'obj': room});




@login_required(login_url='login')    
def deleteMessage(req, pk):
    message = Message.objects.get(id=pk);

    if req.user != message.user:
        return HttpResponse('You are not allowed here!');

    if req.method == 'POST':
        message.delete();
        return redirect('home');
    return render(req, 'base/delete.html', {'obj': message});

@login_required(login_url='login')    
def updateUser(req):
    user = req.user;
    form = UserForm(instance=user);
    context = {'form': form};

    if req.method == 'POST':
        form = UserForm(req.POST, instance=user);
        if form.is_valid():
            form.save();
            return redirect('user-profile', pk=user.id);                        

    return render(req, 'base/update-user.html', context);  

def topicsPage(req):
    topics = Topic.objects.filter();
    context = {'topics': topics};
    return render(req, 'base/topics.html', context);    