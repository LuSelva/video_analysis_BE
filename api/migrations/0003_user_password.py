# Generated by Django 4.1 on 2022-09-06 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_segment_end_time_remove_segment_identifier_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='0000000', max_length=50),
        ),
    ]
