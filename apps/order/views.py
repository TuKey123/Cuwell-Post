from rest_framework import viewsets, status
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

    def list(self, request, *args, **kwargs):
        # customer = stripe.Customer.create(
        #     email="a@gmail.com",
        #     name="Tu",
        #     description="asd",
        #     source="tok_visa_debit",
        # )
        # intent = stripe.PaymentIntent.create(
        #     amount=2000,
        #     currency="usd",
        #     on_behalf_of="acct_1JyJRaIeiMCbzacC"
        # )
        # charge = stripe.Charge.create(
        #     source="tok_visa_debit",
        #     amount=2000,
        #     currency="usd",
        # )
        transfer = stripe.Transfer.create(
            amount=1000,
            currency="usd",
            source_transaction="ch_3K0si9EU1wq10qYa151M3EeA",
            destination="acct_1JyJRaIeiMCbzacC",
        )

        return super(CartViewSet, self).list(request)

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


class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [Authentication]
    serializer_class = serializers.OrderSerializer
    queryset = models.OrderDetail.objects.all()
