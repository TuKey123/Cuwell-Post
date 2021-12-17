from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from core.authentication import Authentication
from . import serializers
from . import models
import paypalrestsdk


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

    def list(self, request, *args, **kwargs):
        # payment = paypalrestsdk.Payment.find('PAYID-MG5BMLA0YA69130BC5796625')
        # payment.execute({'payer_id': 'Q66YGWQ6W7F9J'})

        # paypal_payment = paypalrestsdk.Payment({
        #     "intent": "sale",
        #     "payer": {
        #         "payment_method": "paypal"
        #     },
        #     "redirect_urls": {
        #         "return_url": "http://localhost:3000/payment/execute",
        #         "cancel_url": "http://localhost:3000/"
        #     },
        #     "transactions": [{
        #         "amount": {
        #             "total": 1000,
        #             "currency": "USD"
        #         },
        #     }]
        # })
        # paypal_payment.create()
        # print(paypal_payment.links[1]['href'])

        # payout = paypalrestsdk.Payout({
        #     "sender_batch_header": {
        #         "sender_batch_id": "111",
        #         "email_subject": "You have a payment"
        #     },
        #     "items": [
        #         {
        #             "recipient_type": "EMAIL",
        #             "amount": {
        #                 "value": 100,
        #                 "currency": "USD"
        #             },
        #             "receiver": "sb-jmehf9021208@business.example.com",
        #             "note": "Thank you.",
        #         },
        #         {
        #             "recipient_type": "EMAIL",
        #             "amount": {
        #                 "value": 100,
        #                 "currency": "USD"
        #             },
        #             "receiver": "sb-cynbp9035412@personal.example.com",
        #             "note": "Thank you.",
        #         }
        #     ]
        # })
        # payout.create()
        return super().list(request)

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
        user_id = request.user['id']
        cart = self.get_queryset().filter(post_id=post_id, user=user_id)

        if cart:
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response("this post doesn't exist in cart", status=status.HTTP_400_BAD_REQUEST)


class BuyerOrderViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    authentication_classes = [Authentication]

    def get_queryset(self):
        user = self.request.user['id']
        return models.Order.objects.filter(buyer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.BuyerOrderSerializer
        return serializers.OrderSerializer


class SellerOrderViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.UpdateModelMixin):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    authentication_classes = [Authentication]

    def get_queryset(self):
        user = self.request.user['id']
        return models.Order.objects.filter(post__user=user)

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.SellerOrderSerializer
        return serializers.OrderSerializer


class PaymentViewSet(viewsets.GenericViewSet):
    queryset = models.Payment.objects.all()
    authentication_classes = [Authentication]
    serializer_class = serializers.PaymentExecutionSerializer

    @action(detail=True, methods=['put'], url_path=r'^validate')
    def payment_validate(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuyerCheckOutViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin):
    queryset = models.Order.objects.all()
    serializer_class = serializers.CheckOutSerializer
    authentication_classes = [Authentication]
