from django.db import migrations


def create_demo_posts(apps, schema_editor):
    Post = apps.get_model('main', 'Post')
    if not Post.objects.exists():
        Post.objects.create(
            title='Cyber Adventure',
            content='RPG игра будущего. Можно поставить like или dislike без перезагрузки страницы.'
        )
        Post.objects.create(
            title='Space Battle',
            content='Космический шутер. Счётчики реакций обновляются через JSON.'
        )


def delete_demo_posts(apps, schema_editor):
    Post = apps.get_model('main', 'Post')
    Post.objects.filter(title__in=['Cyber Adventure', 'Space Battle']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_userprofile_alter_likedislike_user'),
    ]

    operations = [
        migrations.RunPython(create_demo_posts, delete_demo_posts),
    ]
