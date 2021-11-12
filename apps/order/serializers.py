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
        user = "2"
        try:
            cart = models.Cart.objects.create(**validated_data, user=user)
            return cart
        except Exception as e:
            raise serializers.ValidationError('create new card unsuccessful')

    class Meta:
        model = models.Cart
        fields = ['id', 'post', 'quantity']


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderDetail
        fields = '__all__'
