from django.db import transaction
from apps.post import models as post_models
from rest_framework import serializers
from django.db.models import F
from . import models
import paypalrestsdk
from datetime import datetime, date, timedelta


# region CART

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = "order_post_image"
        model = post_models.PostImage
        fields = ['id', 'url']


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True)

    class Meta:
        ref_name = "order_post"
        model = post_models.Post
        fields = ['id', 'title', 'price', 'description', 'images']


class CartSerializer(serializers.ModelSerializer):
    post = PostSerializer()

    class Meta:
        model = models.Cart
        fields = '__all__'


class CartCreationSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context['request'].user['id']
        post = attrs.get('post', None)
        if post.user == user:
            raise serializers.ValidationError('can not add to cart your post')

        return super().validate(attrs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user

        return representation

    def create(self, validated_data):
        user = self.context['request'].user['id']
        try:
            post = validated_data.get('post', None)
            quantity = validated_data.get('quantity', None)

            existed_cart = models.Cart.objects.filter(post=post.id, user=user).first()
            if existed_cart:
                existed_cart.quantity += quantity

                if existed_cart.quantity > post.quantity:
                    raise serializers.ValidationError('quantity must be less than stock')

                existed_cart.save()
                return existed_cart

            elif post.quantity >= quantity:
                cart = models.Cart.objects.create(**validated_data, user=user)
                return cart

            raise serializers.ValidationError('quantity must be less than stock')
        except Exception as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = models.Cart
        fields = ['id', 'post', 'quantity', 'payee_email']


# endregion

# region ORDER

def validate_carts_before_order(buyer):
    carts = models.Cart.objects.filter(user=buyer)

    for cart in carts:
        if cart.quantity > cart.post.quantity:
            return False

    return True


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = '__all__'


class BuyerOrderSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        buyer = self.context['request'].user['id']

        if not validate_carts_before_order(buyer):
            serializers.ValidationError('quantity must be less than stock')

        return super().validate(attrs)

    def create_payment(self):
        payment = models.Payment(**self.validated_data)
        payment.save()
        return payment

    def create_orders(self, payment):
        buyer = self.context['request'].user['id']
        carts = models.Cart.objects.filter(user=buyer)
        orders = []

        for cart in carts:
            order = models.Order(price=cart.post.price,
                                 quantity=cart.quantity,
                                 post=cart.post,
                                 buyer=buyer,
                                 payee_email=cart.payee_email,
                                 payment=payment)
            orders.append(order)

        models.Order.objects.bulk_create(orders)
        carts.delete()

        return orders

    def create(self, validated_data):
        try:
            with transaction.atomic():
                payment = self.create_payment()
                orders = self.create_orders(payment)

                return payment
        except Exception as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = models.Payment
        fields = ['id', 'street', 'district', 'city']


class SellerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['delivery_day', 'status']


class PaymentExecutionSerializer(serializers.ModelSerializer):
    def update_post_quantity(self, orders):
        post_ids = list(map(lambda order: order.post.id, orders))
        models.Post.objects.filter(pk__in=post_ids).update(quantity=F('quantity') - 1)

    def detele_carts(self, carts):
        carts.delete()

    def create_orders(self, payment, carts):
        orders = []
        for cart in carts:
            order = models.Order(price=cart.post.price,
                                 quantity=cart.quantity,
                                 post=cart.post,
                                 delivery_day=date.today() + timedelta(days=7),
                                 payee_email=cart.payee_email,
                                 payment=payment)
            orders.append(order)

        models.Order.objects.bulk_create(orders)

        return orders

    def payin(self, paypal_payment, payer_id):
        if not paypal_payment.execute({"payer_id": payer_id}):
            raise serializers.ValidationError('can not execute payment')

    def payout(self, paypal_payment, orders):
        paypal_payout = paypalrestsdk.Payout({
            "sender_batch_header": {
                "sender_batch_id": paypal_payment.id + str(datetime.now()),
                "email_subject": "You have a payment"
            },
            "items": list(map(lambda order:
                              {
                                  "recipient_type": "EMAIL",
                                  "amount": {
                                      "value": order.price * order.quantity,
                                      "currency": "USD"
                                  },
                                  "receiver": order.payee_email,
                                  "note": "You have a payment"
                              }
                              , orders))
        })
        paypal_payout.create()

    def update(self, instance, validated_data):
        payer_id = validated_data.get('payer_id', None)
        paypal_payment = paypalrestsdk.Payment.find(instance.payment_id)
        carts = models.Cart.objects.filter(user=instance.buyer)

        try:
            with transaction.atomic():
                orders = self.create_orders(instance, carts)

                self.update_post_quantity(orders)
                self.detele_carts(carts)

                self.payin(paypal_payment, payer_id)
                self.payout(paypal_payment, orders)

                # update payment
                instance.payer_id = payer_id
                instance.authentication = models.Payment.Status.ACTIVE
                instance.checkout = True
                instance.save()

                return instance
        except Exception as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = models.Payment
        fields = ['payer_id']
        extra_kwargs = {
            'payer_id': {'required': True},
        }


class CheckOutSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['auth_url'] = self.validated_data['auth_url']

        return representation

    def validate(self, attrs):
        buyer = self.context['request'].user['id']

        if not validate_carts_before_order(buyer):
            serializers.ValidationError('quantity must be less than stock')

        return super().validate(attrs)

    def transactions(self, carts):
        total = 0
        for cart in carts:
            total += cart.quantity * cart.post.price

        transactions = [
            {"amount": {
                "total": total,
                "currency": "USD"
            }, }]
        return transactions

    def create_paypal_payment(self, carts):
        paypal_payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "https://cuwell-post-service.herokuapp.com/api/v1/payment/execute",
                "cancel_url": "https://cuwell-post-service.herokuapp.com/api/v1/"
            },
            "transactions": self.transactions(carts)
        })

        if not paypal_payment.create():
            raise serializers.ValidationError(paypal_payment.error)

        return paypal_payment

    def create(self, validated_data):
        buyer = self.context['request'].user['id']
        carts = models.Cart.objects.filter(user=buyer)

        paypal_payment = self.create_paypal_payment(carts)

        self.validated_data['auth_url'] = paypal_payment.links[1]['href']

        payment = models.Payment.objects.create(**validated_data,
                                                payment_id=paypal_payment.id,
                                                buyer=buyer)

        return payment

    class Meta:
        model = models.Payment
        fields = ['id', 'street', 'district', 'city']

# endregion
