# Generated by Django 2.2.2 on 2019-07-04 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='dev',
            field=models.BooleanField(default=False),
        ),
    ]
