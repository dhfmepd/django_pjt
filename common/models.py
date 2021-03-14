from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=50)
    remark = models.TextField()
    sort_no = models.IntegerField()