import uuid
from django.db import models
from django.urls import reverse

class Post(models.Model):
    POST_TYPE_BLOG = "blog"
    POST_TYPE_REJA = "reja"
    POST_TYPE_CHOICES = [
        (POST_TYPE_BLOG, "Blog"),
        (POST_TYPE_REJA, "Reja"),
    ]

    title = models.CharField(max_length=120)  # ✅ 120
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    body = models.TextField(max_length=4000)  # ✅ 4000

    # ✅ blog yoki reja — saytda va Telegramda reja radio ko‘rinishida
    post_type = models.CharField(
        max_length=10, choices=POST_TYPE_CHOICES, default=POST_TYPE_BLOG
    )

    # ✅ Telegram ownership
    owner_telegram_id = models.BigIntegerField(null=True, blank=True, db_index=True)

    # ✅ Private link token
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])
