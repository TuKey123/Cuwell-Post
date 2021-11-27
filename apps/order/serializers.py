from rest_framework import serializers
from . import models


class CartSerializer(serializers.ModelSerializer):
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

            if post.quantity >= quantity:
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
        model = models.OrderDetail
        fields = '__all__'
