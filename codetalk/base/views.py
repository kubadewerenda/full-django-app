from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic
from .forms import RoomForm


# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developers'},
# ]

def loginPage(request):
    #Jesli user juz jest zalogowany to nie moze przejsc na strone loginu
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
    
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)#sprawdza czy dobre dane uzytkoanika zostały podane, jesli nie to zwraca none

        if user is not None:
            login(request, user)#logowanie jesli uzytkownik istnieje
            return redirect('home')
        else:
            messages.error(request, "Username or password is wrong")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)#  usówa token uzytkownika zalogowanego
    return redirect('home')

def registerPage(request):
    #Pobieramy juz gotowy formularz rejestrowania dostepny w django
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occured during registration")

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    #topic__name=q bo w modelsie w room mamy topic i dodajemy __ i name i po tym filtrujemy, a q hbo tak mamy w query search
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |#dzieki Q mozemy dodawac wiecej zaleznosci dzieki ktorym mozemy wyszukiwac
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )#ttuaj zamiast jak wczesniej ze zmiennej room w ktorej jest slownik czyli dane, to pobeiramy z naszej bazy danych i modelu ktory stworzyslismy
    #dzieki icontais sprawdzamy czy q ma wartosc jesli nie ma to zwraca wszsytkie roomy

    room_count = rooms.count()

    topics = Topic.objects.all()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)#przekazujemy stworzone rooms do viewsa

def room(request, pk):
    room = Room.objects.get(id=pk)#pobieramy room o id rownym primarykey z linku
    context = {'room': room}

    return render(request, 'base/room.html', context)

@login_required(login_url='login')#wyswietla jedynie jesli uzytkownik jest zalogowany
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')# bo nadalismy w urls nazwe home dla tego linku op jak cos
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)#instance room czyli obecny pokoj ktory chcemy edytowac

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})