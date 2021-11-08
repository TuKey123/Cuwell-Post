from django.db import transaction
from rest_framework import serializers, status
from . import models


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

    class Meta:
        model = models.Post
        fields = ['id', 'title', 'description', 'price', 'images']


class PostDetailSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, required=False)

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
            if not less_than_2mb(image):
                return False

        return True

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
                user_id = 1
                post = models.Post.objects.create(**data, user=user_id)

                post_images = []
                for image in images:
                    post_image = models.PostImage(url=image, post=post)
                    post_images.append(post_image)

                models.PostImage.objects.bulk_create(post_images)

                validated_data['images'] = list(map(lambda x: {'url': x.url.url}, post_images))

                return validated_data
        except Exception as e:
            raise serializers.ValidationError('can not create post')

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
    class Meta:
        model = models.PostReport
        fields = '__all__'
