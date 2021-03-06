import os
import uuid
from config.settings import base
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    ymd_path = timezone.now().strftime('%Y/%m/%d')
    return os.path.join('upload/'+ymd_path, filename)

class File(models.Model):
    ref_type = models.CharField(max_length=10)
    ref_id = models.IntegerField()
    file_name = models.CharField(max_length=200)
    file_data = models.FileField(upload_to=get_file_path)
    create_date = models.DateTimeField()

    def __str__(self):
        return self.file_name
    
    class Meta:
        verbose_name_plural = '첨부파일'
    
    # 파일 삭제 시 파일데이터 함꼐 삭제
    def delete(self, *args, **kargs):
        if self.file_data:
            os.remove(os.path.join(base.UPLOAD_ROOT, self.file_data.path))
        super(File, self).delete(*args, **kargs)

class Menu(MPTTModel):
    title = models.CharField(max_length=50)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=50, null=True, blank=True)
    argument = models.CharField(max_length=100, null=True, blank=True)
    remark = models.TextField()
    sort_no = models.IntegerField()

    class Meta:
        ordering = ['sort_no', 'lft']
        verbose_name_plural = '메뉴관리'

    class MPTTMeta:
        order_insertion_by = ['sort_no']

    def __str__(self):
        return self.title

class ReceiveHistory(models.Model):
    table_name = models.CharField(max_length=30)
    receive_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    performer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performer_receive_history')
    create_date = models.DateTimeField()
    
    class Meta:
        verbose_name_plural = '수신이력'

class Code(models.Model):
    group_code = models.CharField(max_length=10)
    detail_code = models.CharField(max_length=10)
    detail_code_name = models.CharField(max_length=100)
    reference_value = models.CharField(max_length=50, null=True, blank=True)
    use_flag = models.BooleanField(default=True)
    sort_no = models.IntegerField()
    remark = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '공통코드'



