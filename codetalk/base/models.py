from django.db import models
#from django.contrib.auth.models import User #gotowy model usera przez django
from django.contrib.auth.models import AbstractUser
# Create your models here.
#czyli klasy ktore sa tabelami
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null = True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)#Relacja wiadomosci do roomu w ktorym zostala wpisana, set_null oznacza przypisanie wartosci null gdy topic zostanie usuniety(w ktorym byl room), musi byc null=True zeby mozna przypisac null
    name = models.CharField(max_length=200)
    description = models.CharField(null=True, blank=True)#moze byc puste
    participants = models.ManyToManyField(User, related_name="participants", blank=True)#relacja wielu do wielu
    # ============== MUST HAVE ============== 
    updated = models.DateTimeField(auto_now=True)#Auto uzupełnianie kiedy zapiszemy tabele
    created = models.DateTimeField(auto_now_add=True)#Kierdy tabela zostanie swtworzona

    # ======= Za pomoca tej meta klasy ustawiamy sortowanie od ostatnio dodangeo i zaktualizowanego 
    class Meta:
        ordering = ['-updated', '-created']# jesli damy updated to bedzie sortowane ze zaktualozwany ostatnio bedzie na koncu

    #Gdy chcemy wyprintowac instancje room to bedzie nazwa pokoju
    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)#Relacja wiadomosci do roomu w ktorym zostala wpisana, cascade oznacza uusniecie wiadomosci gdy room zostanie usuniety(w ktorym byla wiadomosc)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)#Auto uzupełnianie kiedy zapiszemy tabele
    created = models.DateTimeField(auto_now_add=True)

    # ======= Za pomoca tej meta klasy ustawiamy sortowanie od ostatnio dodangeo i zaktualizowanego 
    class Meta:
        ordering = ['-updated', '-created']# jesli damy updated to bedzie sortowane ze zaktualozwany ostatnio bedzie na koncu

    def __str__(self):
        return self.body[0:50]#zwracasmy pierwsze 50 znakow wiadomosci