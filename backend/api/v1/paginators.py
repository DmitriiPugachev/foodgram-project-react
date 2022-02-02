"""API v.1 custom paginators."""


from rest_framework.pagination import PageNumberPagination


class PageSizeInParamsPagination(PageNumberPagination):
    """Custom paginator with a page size in query param."""
    page_size_query_param = "limit"
