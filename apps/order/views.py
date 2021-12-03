from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.authentication import Authentication
from . import serializers
from . import models
import stripe

stripe.api_key = "sk_test_51K0raAEU1wq10qYaXMemUPJK7tySdJ3ZnpktTrwTT2BVHyXIbfPDuX3JkzhE3JA8UkdNdetif3SPN9SGV6WZYurO00mIQ0Ek2Z"


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

    @action(detail=False, methods=['delete'], url_path=r'posts/(?P<post_id>\d+)')
    def delete_by_post(self, request, post_id=None):
        cart = self.get_queryset().filter(post_id=post_id)

        if cart:
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response("this post doesn't exist in cart", status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.OrderSerializer
    queryset = models.OrderDetail.objects.all()
