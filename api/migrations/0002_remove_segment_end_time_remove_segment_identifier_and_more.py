# Generated by Django 4.1 on 2022-08-31 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segment',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='segment',
            name='identifier',
        ),
        migrations.RemoveField(
            model_name='segment',
            name='start_time',
        ),
    ]
