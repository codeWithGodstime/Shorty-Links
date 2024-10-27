from django.contrib import admin
from .models import UrlModel, CustomUserModel


class UrlAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'unique_code')


admin.site.register(CustomUserModel)
admin.site.register(UrlModel, UrlAdmin)