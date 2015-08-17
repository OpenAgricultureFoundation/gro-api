from rest_framework.pagination import LimitOffsetPagination

class Pagination(LimitOffsetPagination):
    max_limit = 1000
