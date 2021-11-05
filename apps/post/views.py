from rest_framework import viewsets, mixins, views, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from core.verify_token import verify_token

from . import serializers
from . import models


class PostViewSet(viewsets.GenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin):
    queryset = models.Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.PostSerializer
        elif self.action == "create":
            return serializers.PostCreationSerializer
        return serializers.PostDetailSerializer

    # def list(self, request, *args, **kwargs):
    #     if verify_token(request.META.get('HTTP_AUTHORIZATION')):
    #         return super().list(request, *args, **kwargs)
    #
    #     return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)


class FileUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = serializers.PostCreationSerializer
    queryset = models.Post.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


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
