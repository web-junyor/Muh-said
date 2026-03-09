# Generated migration: remove video field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_add_post_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='video',
        ),
    ]
