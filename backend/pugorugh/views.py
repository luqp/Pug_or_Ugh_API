from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, Http404

from rest_framework.generics import CreateAPIView


from . import serializers


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer
