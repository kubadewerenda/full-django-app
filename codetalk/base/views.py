from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


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
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
    
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)#sprawdza czy dobre dane uzytkoanika zostały podane, jesli nie to zwraca none

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
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
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
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    topics = Topic.objects.all()[0:5]#pierwsze 5 topikow

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)#przekazujemy stworzone rooms do viewsa

def room(request, pk):
    room = Room.objects.get(id=pk)#pobieramy room o id rownym primarykey z linku
    room_messages = room.message_set.all()#tutaj dajemy z malej litery tak jak w modelsach Messages i to zwraca nam wszytskie wiadomosci w relacji z danym roomem
    #-created czyli najnowsze na przodzie
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')#tutaj body bo tak dalismy name w form
        )
        room.participants.add(request.user) 
        return redirect('room', pk=room.id) 

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()#wszystkie roomy uzytkownika
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'topics': topics, 'rooms': rooms, 'room_messages': room_messages}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')#wyswietla jedynie jesli uzytkownik jest zalogowany
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        # Tutaj wyszukuje nam topic jesli juz istnieje to go nam zwraca a jesli nie istnieje to pierw go tworzy a potem zwraca
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)#commit false czyli jeszcze nie wysyla 
        #     room.host = request.user#Przypisujemy usera automatycznie, tego co jest zalogowany
        #     room.save()
        #     return redirect('home')# bo nadalismy w urls nazwe home dla tego linku op jak cos
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)#instance room czyli obecny pokoj ktory chcemy edytowac
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
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

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    
    context = {'form': form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    context = {"topics": topics}
    return render(request, "base/topics.html", context)

def activityPage(request):
    room_messages = Message.objects.all()

    context = {'room_messages': room_messages}
    return render(request, "base/activity.html", context)