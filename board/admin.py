from django.contrib import admin
from .models import Board

class BoardAdmin(admin.ModelAdmin):
    search_fields = ['menu', 'subject']
    list_display = ['menu', 'subject', 'content', 'create_date', 'modify_date']
    list_filter = ['menu']

admin.site.register(Board, BoardAdmin)
