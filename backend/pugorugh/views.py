from django.contrib.auth import get_user_model
from django.shortcuts import Http404

from rest_framework import permissions, viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from .models import Dog, UserPref, UserDog


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class UserPrefView(viewsets.ModelViewSet):
    queryset = UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    @action(detail=False, methods=['get', 'put'])
    def preferences(self, request, pk=None):
        ''' 
            Send user preference data (GET),
            Update user preference data (PUT)
        '''
        try:
            user_pref = UserPref.objects.get(user__id=request.user.id)
        except:
            user_pref = UserPref.objects.create(user=request.user)
        if request.method == "PUT":
            serial = serializers.UserPrefSerializer(
                user_pref, data=request.data)
            serial.is_valid(raise_exception=True)
            serial.save()
        serial = serializers.UserPrefSerializer(user_pref)
        return Response(serial.data)


class StateDogView(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        user_pref = UserPref.objects.get(user_id=user_id)
        return Dog.objects.filter(
            age_status__in=user_pref.age,
            gender__in=user_pref.gender,
            size__in=user_pref.size
        )

    @action(detail=False,
            methods=['get'],
            url_path="(?P<pk>.+)/(?P<dog_status>liked|disliked|undecided)/next")
    def next_dog(self, request, pk=None, dog_status=None):
        '''
            Send the data of the next dog with id greater than pk
            that is in one of the dog_status groups.
        '''
        favorite_dogs = self.get_queryset()
        try:
            pk = int(pk)
        except ValueError:
            raise Http404
        dogs = favorite_dogs.filter(
            userdog__status=dog_status[0],
            userdog__user__id=request.user.id
        )
        dog = dogs.filter(id__gt=pk).first()
        if not dog:
            dog = dogs.first()
        if dog:
            serializer = serializers.DogSerializer(dog)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False,
            methods=['put'],
            url_path="(?P<pk>\d+)/(?P<dog_status>liked|disliked|undecided)")
    def status_update(self, request, pk=None, dog_status=None):
        '''
            Update the state of the dog with id = pk 
            to the one indicated in dog_status.
        '''
        user_dog = UserDog.objects.filter(
            user__id=request.user.id,
            dog__id=self.kwargs.get('pk')
        ).update(status=dog_status[0])
        return Response(status=status.HTTP_204_NO_CONTENT)
