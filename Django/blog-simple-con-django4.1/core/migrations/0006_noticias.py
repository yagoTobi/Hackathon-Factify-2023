# Generated by Django 5.0.2 on 2024-02-29 00:21

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_post_author_alter_post_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Noticias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Título')),
                ('excerpt', models.TextField(verbose_name='Bajada')),
                ('content', ckeditor.fields.RichTextField(verbose_name='Contenido')),
            ],
        ),
    ]
