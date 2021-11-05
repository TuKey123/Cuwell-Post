from rest_framework import serializers
from . import models


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


class PostCreationSerializer(serializers.Serializer):
    images = serializers.FileField(required=False)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    price = serializers.FloatField(min_value=1)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


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
