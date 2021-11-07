from rest_framework import viewsets, mixins, views, status
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
        else:
            return serializers.PostAlterationSerializer

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
