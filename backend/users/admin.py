from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
    )
    search_fields = ("name",)
    list_filter = ("username", "email",)
    empty_value_display = "-empty-"


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
