# Generated by Django 3.2.7 on 2021-09-11 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('publicName', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateTime', models.DateTimeField()),
                ('word', models.CharField(max_length=30)),
                ('lemme', models.CharField(max_length=30)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.channel')),
            ],
        ),
    ]
