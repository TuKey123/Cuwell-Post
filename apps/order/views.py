from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.authentication import Authentication

from . import serializers
from . import models


class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.CartSerializer
    queryset = models.Cart.objects.all()

    def get_serializer_class(self):
        if self.action == 'detail':
            return serializers.OrderDetailSerializer
        elif self.action == 'create':
            return serializers.CartCreationSerializer
        return serializers.CartSerializer

    # @action(detail=True, methods=['get'])
    # def detail(self, request, pk):
    #     try:
    #         print('11111111')
    #         order_detail = models.OrderDetail.objects.get(=pk)
    #         return Response(order_detail, status=status.HTTP_200_OK)
    #
    #     except ObjectDoesNotExist:
    #         return Response('order id is invalid', status=status.HTTP_400_BAD_REQUEST)


class OrderDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.OrderDetailSerializer
    queryset = models.OrderDetail.objects.all()
