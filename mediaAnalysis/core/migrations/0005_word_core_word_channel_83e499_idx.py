# Generated by Django 3.2.7 on 2021-10-17 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210912_0919'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='word',
            index=models.Index(fields=['channel'], name='core_word_channel_83e499_idx'),
        ),
    ]
