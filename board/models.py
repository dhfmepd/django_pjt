from django.db import models
from django.contrib.auth.models import User
from common.models import Menu

class Board(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_board')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_board')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_board')

    def __str__(self):
        return self.subject

class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_reply')
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_reply')

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    board = models.ForeignKey(Board, null=True, blank=True, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE)
