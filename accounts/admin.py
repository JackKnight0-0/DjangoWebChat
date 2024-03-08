from django.contrib import admin

from .models import CustomUser, Status


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['user', ]
    readonly_fields = ['status', ]
