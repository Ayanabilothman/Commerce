# Generated by Django 4.0.1 on 2022-02-10 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_remove_comment_comment_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_time',
            field=models.DateTimeField(default='2022-02-11 02:12:50'),
        ),
    ]
