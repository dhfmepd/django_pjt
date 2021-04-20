import os
import uuid
from config.settings.base import base
from django.utils import timezone
from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=50)
    remark = models.TextField()
    sort_no = models.IntegerField()

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
    
    # 파일 삭제 시 파일데이터 함꼐 삭제
    def delete(self, *args, **kargs):
        if self.file_data:
            os.remove(os.path.join(base.UPLOAD_ROOT, self.file_data.path))
        super(File, self).delete(*args, **kargs)