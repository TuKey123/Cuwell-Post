from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from . import models
from apps.order import models as order_models

import requests


# EXTRA FUNC
def less_than_2mb(image):
    # convert to Mb
    size = image.size / (1024 ** 2)

    if size > 2:
        return False
    return True


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostImage
        fields = ['id', 'url']


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['total'] = instance.quantity
        representation['sell'] = instance.orders.filter(Q(payment__checkout=True) |
                                                        Q(status=order_models.Order.Status.DELIVERED)).count()
        representation['stock'] = representation['total']

        return representation

    class Meta:
        model = models.Post
        fields = ['id', 'title', 'description', 'price', 'status', 'user', 'quantity', 'images', 'category']


class PostDetailSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, required=False)

    def user_detail(self):
        try:
            user_id = self.instance.user
            token = self.context['request'].META.get('HTTP_AUTHORIZATION').split(' ')[1]
            url = settings.AUTH_SERVICE_URL + user_id

            headers = {
                'Authorization': 'Bearer {}'.format(token)
            }
            response = requests.get(url, headers=headers)

            if response.json()['statusCode'] != 200:
                raise serializers.ValidationError('can not fetch user information')

            data = response.json()['payload']

            return {
                "id": user_id,
                "email": data['email'],
                "name": data['name'],
                "phone": data['phone'],
                "rating": data['ratingAverage'],
                "address": data['address'],
                'paypalEmail': data['paypalEmail']
            }
        except Exception as e:
            raise serializers.ValidationError(e)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['total'] = instance.quantity
        representation['sell'] = instance.orders.filter(Q(payment__checkout=True) |
                                                        Q(status=order_models.Order.Status.DELIVERED)).count()
        representation['stock'] = representation['total']
        representation['user'] = self.user_detail()

        representation.pop('quantity')
        return representation

    class Meta:
        model = models.Post
        fields = '__all__'


class PostCreationSerializer(serializers.ModelSerializer):
    def validate_images(self):
        images = self.initial_data.getlist('images', None)

        if not images:
            return True
        elif len(images) > 3:
            return False

        for image in images:
            if not image:
                raise serializers.ValidationError('image can not be null')

            elif not less_than_2mb(image):
                return False

        return True

    def validate_quantity(self, value):
        if value > 0:
            return value
        raise serializers.ValidationError('quantity can not be less than 1')

    def validate(self, attrs):
        if not self.validate_images():
            raise serializers.ValidationError('image must be less than 2mb')

        return super().validate(attrs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = instance['images']

        return representation

    def create(self, validated_data):
        data = validated_data.copy()
        images = self.initial_data.getlist('images', None)
        try:
            with transaction.atomic():
                user = self.context['request'].user['id']
                post = models.Post.objects.create(**data, user=user)

                post_images = []
                for image in images:
                    post_image = models.PostImage(url=image, post=post)
                    post_images.append(post_image)

                models.PostImage.objects.bulk_create(post_images)

                validated_data['images'] = list(map(lambda x: {'id': x.id, 'url': x.url.url}, post_images))

                return validated_data
        except Exception as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = models.Post
        fields = ['title', 'description', 'price', 'category', 'quantity']


class PostPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ['title', 'description', 'price', 'category', 'quantity']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'category': {'required': False},
            'price': {'required': False},
            'quantity': {'required': False}
        }


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ['title', 'description', 'price', 'category', 'quantity']


class PostImageUpdateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        image = attrs.get('url', None)

        if not image:
            raise serializers.ValidationError('image can not be none')
        elif not less_than_2mb(image):
            raise serializers.ValidationError('image must be less than 2mb')

        return super().validate(attrs)

    def update(self, instance, validated_data):
        instance.url.delete()

        instance.url = validated_data.get('url', None)
        instance.save()

        return instance

    class Meta:
        model = models.PostImage
        fields = ['url']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class ReportTypeSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        type_id = representation['type']

        representation['type_name'] = models.ReportType.Type.names[type_id - 1]
        return representation

    class Meta:
        model = models.ReportType
        fields = '__all__'


class PostReportSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context['request'].user['id']
        validated_data['user'] = user

        return super().create(validated_data)

    class Meta:
        model = models.PostReport
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }


class BlockPostSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        instance.is_blocked = validated_data['is_blocked']
        return instance

    class Meta:
        model = models.Post
        fields = ['is_blocked']
        extra_kwargs = {
            'is_blocked': {'required': True}
        }
