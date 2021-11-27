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

    def get_queryset(self):
        user_id = self.request.user['id']
        query = super().get_queryset()
        return query.filter(user=user_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CartCreationSerializer
        return serializers.CartSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.user['id']
        instance = self.get_object()

        if user_id != instance.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, *kwargs)

    def destroy(self, request, *args, **kwargs):
        user_id = request.user['id']
        instance = self.get_object()

        if user_id != instance.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
