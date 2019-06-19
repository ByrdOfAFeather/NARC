# Generated by Django 2.2.2 on 2019-06-19 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('date_created', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashed_token', models.CharField(max_length=65, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserToDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CanvasWrapper.Dataset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CanvasWrapper.User')),
            ],
        ),
    ]
