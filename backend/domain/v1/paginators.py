from rest_framework.pagination import PageNumberPagination


class LimitInParamsPagination(PageNumberPagination):
    page_size_query_param = "limit"
