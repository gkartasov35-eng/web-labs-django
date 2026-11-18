from django.db import migrations, models


def link_existing_posts(apps, schema_editor):
    posts = apps.get_model('main', 'Post').objects.using(schema_editor.connection.alias)
    for title, key in (('Cyber Adventure', 'cyber-adventure'), ('Space Battle', 'space-battle')):
        post = posts.filter(title=title).order_by('pk').first()
        if post is not None:
            posts.filter(pk=post.pk).update(catalog_key=key)


class Migration(migrations.Migration):
    dependencies = [('main', '0004_create_demo_posts')]

    operations = [
        migrations.AddField(
            model_name='post',
            name='catalog_key',
            field=models.SlugField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.RunPython(link_existing_posts, migrations.RunPython.noop),
    ]
