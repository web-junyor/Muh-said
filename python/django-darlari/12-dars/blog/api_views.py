from datetime import timedelta
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Post
from .serializers import PostCreateSerializer
from .auth import BotApiKeyAuthentication

User = get_user_model()


def _base_site_url(request):
    """Boshqa qurilmalar ham saytga kira olishi uchun PUBLIC_SITE_URL ishlatiladi."""
    base = getattr(settings, "PUBLIC_SITE_URL", "").rstrip("/")
    if base:
        return base
    return request.build_absolute_uri("/").rstrip("/")


def get_telegram_bot_user():
    # bot postlari uchun service user
    user, _ = User.objects.get_or_create(username="telegram_bot")
    return user

class PostListCreateApi(APIView):
    """GET = ro'yxat, POST = yangi post yaratish. Ikkalasi /api/posts/ da. Rasm multipart/form-data da."""
    authentication_classes = [BotApiKeyAuthentication]
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        owner_id = request.query_params.get("owner_telegram_id")
        if not owner_id:
            return Response(
                {"error": "owner_telegram_id kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            owner_id = int(owner_id)
        except ValueError:
            return Response(
                {"error": "owner_telegram_id son bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        posts = Post.objects.filter(owner_telegram_id=owner_id)
        last_hours = request.query_params.get("last_hours")
        if last_hours:
            try:
                hours = int(last_hours)
                if hours > 0:
                    since = timezone.now() - timedelta(hours=hours)
                    posts = posts.filter(created_at__gte=since)
            except ValueError:
                pass
        posts = posts.order_by("-created_at")
        result = []
        base = _base_site_url(request)
        for post in posts:
            path = reverse("post_detail", args=[post.id])
            private_url = f"{base}{path}?t={post.access_token}"
            image_url = request.build_absolute_uri(post.image.url) if post.image else None
            result.append({
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "image_url": image_url,
                "access_token": str(post.access_token),
                "private_url": private_url,
                "post_type": getattr(post, "post_type", "blog"),
            })
        return Response(result)

    def post(self, request):
        # Multipart dan kelganda title/body ro'yxat bo'lishi mumkin — serializer string kutadi
        raw = dict(request.data) if request.data else {}
        data = {}
        for key, value in raw.items():
            if key == "image":
                continue
            if isinstance(value, list) and len(value) > 0:
                data[key] = value[0]
            else:
                data[key] = value
        if request.FILES.get("image"):
            data["image"] = request.FILES["image"]
        serializer = PostCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        bot_user = get_telegram_bot_user()
        post = serializer.save(author=bot_user)

        path = reverse("post_detail", args=[post.id])
        base = _base_site_url(request)
        private_url = f"{base}{path}?t={post.access_token}"

        data = PostCreateSerializer(post).data
        data["private_url"] = private_url
        return Response(data, status=status.HTTP_201_CREATED)


class PostDeleteApi(APIView):
    authentication_classes = [BotApiKeyAuthentication]
    permission_classes = []

    def delete(self, request, pk):
        token = request.data.get("access_token") or request.query_params.get("access_token")
        if not token:
            return Response(
                {"error": "access_token kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            post = Post.objects.get(pk=pk, access_token=token)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post topilmadi yoki token noto'g'ri"},
                status=status.HTTP_404_NOT_FOUND,
            )
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
