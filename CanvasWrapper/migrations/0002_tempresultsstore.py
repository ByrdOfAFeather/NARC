# Generated by Django 2.2.2 on 2019-07-15 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CanvasWrapper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempResultsStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.IntegerField(unique=True)),
                ('cheaters', models.TextField()),
                ('non_cheaters', models.TextField()),
            ],
        ),
    ]
