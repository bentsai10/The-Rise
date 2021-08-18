# Generated by Django 3.0.7 on 2021-08-18 00:07

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('link', models.CharField(max_length=200)),
                ('link_title', models.CharField(max_length=255)),
                ('participant_cap', models.IntegerField()),
                ('participants', models.IntegerField(default=1)),
                ('audio', models.FileField(upload_to=main.models.discussion_upload_to)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'discussion_posts',
            },
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'network',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=17)),
                ('essay', models.TextField()),
                ('referral', models.CharField(max_length=255)),
                ('password', models.CharField(blank=True, max_length=255)),
                ('year', models.CharField(blank=True, max_length=4)),
                ('department1', models.CharField(blank=True, max_length=255)),
                ('department2', models.CharField(blank=True, max_length=255)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('profile_picture', models.ImageField(blank=True, upload_to=main.models.upload_to)),
                ('permissions', models.IntegerField(default=0)),
                ('status', models.BooleanField(default=False)),
                ('verification_code', models.CharField(blank=True, max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('favorited_users', models.ManyToManyField(related_name='favorite_spaces', to='main.User')),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Network')),
            ],
            options={
                'db_table': 'spaces',
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.FileField(upload_to=main.models.response_upload_to)),
                ('link', models.CharField(blank=True, max_length=200)),
                ('link_title', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='response_posts', to='main.Discussion')),
                ('poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='response_posts', to='main.User')),
            ],
            options={
                'db_table': 'response_posts',
            },
        ),
        migrations.AddField(
            model_name='discussion',
            name='poster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_posts', to='main.User'),
        ),
        migrations.AddField(
            model_name='discussion',
            name='saved_users',
            field=models.ManyToManyField(related_name='saved_discussions', to='main.User'),
        ),
        migrations.AddField(
            model_name='discussion',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_posts', to='main.Space'),
        ),
    ]
