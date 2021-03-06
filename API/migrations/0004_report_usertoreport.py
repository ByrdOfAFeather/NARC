# Generated by Django 2.2.2 on 2019-08-05 18:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('API', '0003_delete_notificationtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_desc', models.TextField()),
                ('report_date', models.DateField(auto_now_add=True)),
                ('report_addressed', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserToReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Report')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
