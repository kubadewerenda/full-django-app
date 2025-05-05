from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "GET /api/",
        "GET /api/rooms",
        "GET /api/rooms/:id",
    ]
    return Response(routes)#Safe false ze mozemy dac liste a nie tylko dict

@api_view(["GET"])
def getRooms(request):
    rooms = Room.objects.all()#serializer zamienia z pythonowych danych na dane w formacie json
    serializer = RoomSerializer(rooms, many=True)#duzo obiektow

    return Response(serializer.data)

@api_view(["GET"])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)#serializer zamienia z pythonowych danych na dane w formacie json
    serializer = RoomSerializer(room, many=False)#1 obiekt bo false

    return Response(serializer.data)