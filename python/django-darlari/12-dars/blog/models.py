from django.db import models
from django.urls import reverse
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    body = models.TextField()
# bunda foydalanuvchi o'chirilganda uning barcha postlari ham o'chiriladi



    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])