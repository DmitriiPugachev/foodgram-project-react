from django.urls import include, path

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.urls.jwt")),
    path("users/", include("users.v1.urls")),
    path("", include("domain.v1.urls"))
]
