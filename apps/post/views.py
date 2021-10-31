from rest_framework import viewsets
from . import serializers
from . import models


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PostSerializer
    queryset = models.Post.objects.all()
