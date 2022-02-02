"""API v.1 custom mixins."""


from rest_framework import mixins, viewsets


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Custom ViewSet only for POST and GET methods."""
    pass
