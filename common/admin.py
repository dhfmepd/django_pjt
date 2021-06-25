from django.contrib import admin
from .models import Menu, File, ReceiveHistory, Code
from mptt.admin import DraggableMPTTAdmin

class FileAdmin(admin.ModelAdmin):
    search_fields = ['file_name']

class ReceiveHistoryAdmin(admin.ModelAdmin):
    search_fields = ['table_name']

class CodeAdmin(admin.ModelAdmin):
    search_fields = ['group_code']

admin.site.register(File, FileAdmin)
admin.site.register(Menu, DraggableMPTTAdmin)
admin.site.register(ReceiveHistory, ReceiveHistoryAdmin)
admin.site.register(Code, CodeAdmin)
