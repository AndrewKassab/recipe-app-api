# Generated by Django 3.2.25 on 2024-07-17 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20240717_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='name',
            field=models.CharField(default='Eggplant', max_length=255),
            preserve_default=False,
        ),
    ]
