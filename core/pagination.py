from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class StandardPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        page_number = self.page.number
        page_size = self.get_page_size(self.request)

        return Response(OrderedDict([
            ('count', count),
            ('pageIndex', page_number),
            ('pageSize', page_size),
            ('pageNumber', math.ceil(count / page_size)),
            ('results', data)
        ]))
