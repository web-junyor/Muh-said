from rest_framework import serializers
from .models import Post

class PostCreateSerializer(serializers.ModelSerializer):
    owner_telegram_id = serializers.IntegerField()
    post_type = serializers.ChoiceField(choices=Post.POST_TYPE_CHOICES, default=Post.POST_TYPE_BLOG, required=False)

    class Meta:
        model = Post
        fields = ["id", "title", "body", "image", "owner_telegram_id", "access_token", "created_at", "post_type"]
        read_only_fields = ["id", "access_token", "created_at"]

    def validate_title(self, v):
        v = v.strip()
        if len(v) < 3:
            raise serializers.ValidationError("Title juda qisqa.")
        if len(v) > 120:
            raise serializers.ValidationError("Title 120 dan oshmasin.")
        return v

    def validate_body(self, v):
        v = v.strip()
        if len(v) < 10:
            raise serializers.ValidationError("Body juda qisqa.")
        if len(v) > 4000:
            raise serializers.ValidationError("Body 4000 dan oshmasin.")
        return v
