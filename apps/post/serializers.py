from rest_framework import serializers
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
        fields = ['url']


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


class PostAlterationSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    def validate(self, attrs):
        image = attrs.get('image', None)

        if not image:
            return super().validate(attrs)
        elif not less_than_2mb(image):
            raise serializers.ValidationError('image must be less than 2mb')

        return super().validate(attrs)

    def create(self, validated_data):
        data = validated_data.copy()
        image = data.pop('image')

        post = models.Post.objects.create(**data)
        post_image = models.PostImage.objects.create(url=image, post=post)

        validated_data['image'] = post_image.url

        return validated_data

    class Meta:
        model = models.Post
        fields = ['title', 'description', 'price', 'user', 'category', 'image']


class PostPartialSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    def validate(self, attrs):
        image = attrs.get('image', None)

        if not image:
            return super().validate(attrs)
        elif not less_than_2mb(image):
            raise serializers.ValidationError('image must be less than 2mb')

        return super().validate(attrs)

    class Meta:
        model = models.Post
        fields = ['title', 'description', 'price', 'user', 'category', 'image']
        extra_kwargs = {'title': {'required': False},
                        'description': {'required': False},
                        'user': {'required': False},
                        'category': {'required': False},
                        'price': {'required': False}}


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
