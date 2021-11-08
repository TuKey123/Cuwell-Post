from rest_framework import viewsets, mixins, views, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db import transaction, IntegrityError, Error

from . import serializers
from . import models


class PostCreateViewSet(viewsets.ModelViewSet):
    queryset = models.Post.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostSerializer
        elif self.action == 'retrieve':
            return serializers.PostDetailSerializer
        elif self.action == 'partial_update':
            return serializers.PostPartialSerializer
        elif self.action == 'update':
            return serializers.PostUpdateSerializer
        elif self.action == 'update_image':
            return serializers.PostImageUpdateSerializer
        else:
            return serializers.PostCreationSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                post_id = kwargs['pk']
                post = models.Post.objects.get(id=post_id)

                if post.images.all():
                    for image in post.images.all():
                        image.url.delete()

                    post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except IntegrityError as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Error as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path=r'update_image/(?P<image_id>\d+)')
    def update_image(self, request, image_id=None):
        image_instance = models.PostImage.objects.get(id=image_id)

        serializer = self.get_serializer(image_instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class PostImageUpdate(viewsets.GenericViewSet,
                      mixins.UpdateModelMixin):
    serializer_class = serializers.PostImageUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()


class ReportTypeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin):
    serializer_class = serializers.ReportTypeSerializer
    queryset = models.ReportType.objects.all()


class PostReportViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin):
    serializer_class = serializers.PostReportSerializer
    queryset = models.PostReport.objects.all()
