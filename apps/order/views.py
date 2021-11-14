from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.authentication import Authentication

from . import serializers
from . import models
from .producer import publish


class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.CartSerializer
    queryset = models.Cart.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CartCreationSerializer
        return serializers.CartSerializer

    def list(self, request, *args, **kwargs):
        publish('Phan anh tu')
        return super().list(request)

    @action(detail=False, methods=['get'], url_path=r'^users/(?P<user_id>\w{0,50})')
    def get_user_orders(self, request, user_id):
        try:
            carts = models.Cart.objects.filter(user=user_id)
            serializer = self.get_serializer(carts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response('userId is invalid', status=status.HTTP_400_BAD_REQUEST)


class OrderDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.OrderDetailSerializer
    queryset = models.OrderDetail.objects.all()
