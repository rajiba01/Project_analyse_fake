from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("email", "firstName", "lastName", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")

    ordering = ("email",)
    search_fields = ("email", "firstName", "lastName")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("firstName", "lastName")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "firstName", "lastName", "password1", "password2", "is_staff", "is_active"),
        }),
    )