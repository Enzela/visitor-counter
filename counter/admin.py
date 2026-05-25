from django.contrib import admin
from .models import VisitorLog

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'timestamp']
    list_filter = ['timestamp']
    ordering = ['-timestamp']