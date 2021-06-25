from django.contrib import admin
from .models import Menu, File, ReceiveHistory, Code
from mptt.admin import DraggableMPTTAdmin

class FileAdmin(admin.ModelAdmin):
    search_fields = ['file_name']
    list_display = ['ref_type', 'ref_id', 'file_name', 'file_data', 'create_date']
    list_filter = ['ref_type']

class ReceiveHistoryAdmin(admin.ModelAdmin):
    search_fields = ['table_name']
    list_display = ['table_name', 'receive_count', 'total_count', 'performer', 'create_date']
    list_filter = ['table_name']

class CodeAdmin(admin.ModelAdmin):
    search_fields = ['group_code']
    list_display = ['group_code', 'detail_code', 'detail_code_name', 'reference_value', 'use_flag', 'sort_no']
    list_filter = ['group_code']

admin.site.register(File, FileAdmin)
admin.site.register(Menu, DraggableMPTTAdmin)
admin.site.register(ReceiveHistory, ReceiveHistoryAdmin)
admin.site.register(Code, CodeAdmin)
