# Generated by Django 3.0.7 on 2021-08-08 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20210808_0520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='participants',
            field=models.IntegerField(default=1),
        ),
    ]
