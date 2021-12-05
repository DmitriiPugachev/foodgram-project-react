from rest_framework import filters, mixins, status, viewsets
from django.contrib.auth import get_user_model
from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import CustomGetUserSerializer, CustomCreateUserSerializer

User = get_user_model()


class CreateListRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    serializer_class = CustomGetUserSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return CustomGetUserSerializer
        return CustomCreateUserSerializer

    @action(
        detail=False,
        methods=["get"],
        url_name="me",
        # permission_classes=(IsAuthenticated,),
        serializer_class=CustomGetUserSerializer,
    )
    def me(self, request):
        user_me = User.objects.get(username=self.request.user.username)
        serializer = self.get_serializer(user_me)
        return Response(serializer.data, status=status.HTTP_200_OK)
