from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Sum, F
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db import transaction, IntegrityError, Error
from rest_framework.views import APIView

from core.authentication import Authentication, AdminPermission
from core.pagination import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import date

from . import serializers
from . import models
from apps.order import models as order_models


class SearchAutoComplete(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset


class PostViewSet(viewsets.ModelViewSet):
    queryset = models.Post.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [Authentication]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'price']
    filterset_fields = ['category']

    def get_queryset(self):
        return models.Post.objects.filter(quantity__gt=0, is_blocked=False).order_by('id').reverse()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'get_posts_by_user_id':
            return serializers.PostSerializer
        elif self.action == 'retrieve':
            return serializers.PostDetailSerializer
        elif self.action == 'partial_update':
            return serializers.PostPartialSerializer
        elif self.action == 'update':
            return serializers.PostUpdateSerializer
        elif self.action == 'update_image':
            return serializers.PostImageUpdateSerializer
        elif self.action == 'block_post':
            return serializers.BlockPostSerializer
        else:
            return serializers.PostCreationSerializer

    def get_permissions(self):
        if self.action == 'block_post':
            return [AdminPermission()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user_id = request.user['id']
                post_id = kwargs['pk']
                post = models.Post.objects.get(id=post_id, user=user_id)

                if post.images.all():
                    for image in post.images.all():
                        image.url.delete()

                post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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

    @action(detail=False, methods=['get'], url_path=r'^users/(?P<user_id>[\w\-]+)')
    def get_posts_by_user_id(self, request, user_id=None):
        queryset = models.Post.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['put'], url_path='block')
    def block_post(self, request, pk=None):
        instance = models.Post.objects.filter(pk=pk).first()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostAutoCompleteViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'price']
    filterset_fields = ['category']

    def get_queryset(self):
        return models.Post.objects.filter(quantity__gt=0, is_blocked=False).order_by('id').reverse().only('title',
                                                                                                          'description',
                                                                                                          'price')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_param = request.query_params.get('search', None)
        if not search_param:
            return Response([], status=status.HTTP_200_OK)

        try:
            search_param = search_param.lower()
            queryset = queryset.filter(Q(title__istartswith=search_param) |
                                       Q(description__istartswith=search_param))

            auto_complete = []

            for record in queryset:
                if search_param in record.title.lower():
                    result = ' '.join(record.title.split(' ')[0:7])
                    auto_complete.append(result)
                elif search_param in record.description.lower():
                    result = ' '.join(record.description.split(' ')[0:7])
                    auto_complete.append(result)

            return Response(list(set(auto_complete)), status=status.HTTP_200_OK)

        except Exception as e:
            return Response([], status=status.HTTP_200_OK)


class PostImageUpdate(viewsets.GenericViewSet,
                      mixins.UpdateModelMixin):
    serializer_class = serializers.PostImageUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [Authentication]


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = [Authentication]


class ReportTypeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin):
    queryset = models.ReportType.objects.all()
    serializer_class = serializers.ReportTypeSerializer
    authentication_classes = [Authentication]


class PostReportViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin):
    queryset = models.PostReport.objects.all()
    serializer_class = serializers.PostReportSerializer
    authentication_classes = [Authentication]


class StatisticViewSet(viewsets.GenericViewSet):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    authentication_classes = [Authentication]
    permission_classes = [AdminPermission]

    def get_queryset(self):
        if self.action == 'get_payments_by_month':
            return order_models.Order.objects.all()
        return models.Post.objects.all()

    @action(detail=False, methods=['get'], url_path=r'^users/number-of-posts')
    def get_posts_by_user(self, request):
        queryset = self.get_queryset()
        queryset = queryset.values('user').annotate(number_of_posts=Count('user')).order_by('-number_of_posts')
        data = list(queryset)

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'^users/number-of-orders')
    def get_orders_by_user(self, request):
        queryset = order_models.Order.objects.values('user').annotate(number_of_orders=Count('user')).order_by(
            '-number_of_orders')
        data = list(queryset)

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'^categories/number-of-posts')
    def get_posts_by_category(self, request):
        queryset = self.get_queryset()
        queryset = queryset.values('category', 'category__name').annotate(number_of_posts=Count('category'), ).order_by(
            '-number_of_posts')
        data = list(queryset)

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'^posts/by-month')
    def get_posts_by_month(self, request):
        month = date.today().month
        previous_month = month - 1

        current = self.get_queryset().filter(created_at__month=month).count()
        previous = self.get_queryset().filter(created_at__month=previous_month).count()

        data = {
            'current': current,
            'previous': previous,
        }

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'^payments/by-month')
    def get_payments_by_month(self, request):
        month = date.today().month
        previous_month = month - 1

        current = self.get_queryset().filter(created_at__month=month).values('created_at').aggregate(
            total=Sum(F('price') * F('quantity')))['total']

        previous = self.get_queryset().filter(created_at__month=previous_month).values('created_at').aggregate(
            total=Sum(F('price') * F('quantity')))['total']

        data = {
            'current': current or 0,
            'previous': previous or 0,
        }

        return Response(data=data, status=status.HTTP_200_OK)
