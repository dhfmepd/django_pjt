import csv
from django.contrib import admin
from django.http import HttpResponse
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
    actions = ["export_as_csv"]
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "CSV Export Selected"


admin.site.register(File, FileAdmin)
admin.site.register(Menu, DraggableMPTTAdmin)
admin.site.register(ReceiveHistory, ReceiveHistoryAdmin)
admin.site.register(Code, CodeAdmin)
