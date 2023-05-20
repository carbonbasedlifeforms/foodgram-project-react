from rest_framework import pagination


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """Класс кастомной пагинации"""
    page_size_query_param = 'limit'
