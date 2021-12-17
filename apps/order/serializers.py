import paypalrestsdk
from apps.post import models as post_models
from rest_framework import serializers
from . import models


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
        fields = ['id', 'post', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = '__all__'


class BuyerOrderSerializer(serializers.ModelSerializer):
    def validate_quantity(self, quantity):
        post_id = self.initial_data.get('post', None)
        post = post_models.Post.objects.get(pk=post_id)

        if post.quantity < quantity:
            raise serializers.ValidationError('quantity must be less than stock')

        return True

    def create(self, validated_data):
        try:
            buyer = self.context['request'].user['id']
            order = models.Order.objects.create(**validated_data, buyer=buyer)
            return validated_data
        except Exception as e:
            raise serializers.ValidationError('can not order')

    class Meta:
        model = models.Order
        fields = '__all__'
        extra_kwargs = {
            'buyer': {'read_only': True},
            'delivery_day': {'read_only': True},
            'status': {'read_only': True},
        }


class SellerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['delivery_day', 'status']


class PaymentExecutionSerializer(serializers.ModelSerializer):
    # def create_orders(self):
    #     orders = []
    #     carts = models.Cart.objects.filter()
    #     for cart in carts:
    #         order = models.Order(**validated_data,
    #                              price=cart.post.price,
    #                              quantity=cart.quantity,
    #                              post=cart.post,
    #                              buyer=buyer,
    #                              payee_email=cart.payee_email,
    #                              payment=payment)
    #         orders.append(order)
    #     models.Order.objects.bulk_create(orders)
    #     carts.delete()
    #     return orders

    def update(self, instance, validated_data):
        payer_id = validated_data.get('payer_id', None)

        payment = paypalrestsdk.Payment.find(instance.payment_id)

        if not payment.execute({"payer_id": payer_id}):
            raise serializers.ValidationError('can not execute payment')

        instance.payer_id = payer_id
        instance.authentication = models.Payment.Status.ACTIVE

        instance.save()

        return instance

    class Meta:
        model = models.Payment
        fields = ['payer_id']
        extra_kwargs = {
            'payer_id': {'required': True},
        }


class CheckOutSerializer(serializers.ModelSerializer):
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

    def create_payment(self, payment_id):
        payment = models.Payment(payment_id=payment_id)
        payment.save()
        return payment

    def create_paypal_payment(self, carts):
        paypal_payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://localhost:3000/payment/execute",
                "cancel_url": "http://localhost:3000/"
            },
            "transactions": self.transactions(carts)
        })

        if not paypal_payment.create():
            raise serializers.ValidationError('can not create payment instance')

        return paypal_payment

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['auth_url'] = self.validated_data['auth_url']

        return representation

    def create(self, validated_data):
        buyer = self.context['request'].user['id']
        carts = models.Cart.objects.filter(user=buyer)

        paypal_payment = self.create_paypal_payment(carts)
        payment = self.create_payment(payment_id=paypal_payment.id)

        # get authentication url
        self.validated_data['auth_url'] = paypal_payment.links[1]['href']

        return validated_data

    class Meta:
        model = models.Order
        fields = ['street', 'district', 'city']
