from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=50)
    remark = models.TextField()
    sort_no = models.IntegerField()


class File(models.Model):
    ref_type = models.CharField(max_length=10)
    ref_id = models.IntegerField()
    file_name = models.CharField(max_length=200)
    file_data = models.FileField(upload_to='upload/%Y/%m/%d')
    create_date = models.DateTimeField()

    def __str__(self):
        return self.file_name