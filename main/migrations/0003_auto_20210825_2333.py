# Generated by Django 3.0.7 on 2021-08-25 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_space_network'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='verification_code',
        ),
        migrations.AddField(
            model_name='discussion',
            name='duration',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='response',
            name='duration',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='participants',
        ),
        migrations.CreateModel(
            name='ParticipantInDiscussion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Discussion')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.User')),
            ],
        ),
        migrations.AddField(
            model_name='discussion',
            name='participants',
            field=models.ManyToManyField(related_name='discussions_participated_in', through='main.ParticipantInDiscussion', to='main.User'),
        ),
    ]
