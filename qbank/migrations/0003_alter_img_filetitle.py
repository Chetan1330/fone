# Generated by Django 4.1 on 2022-11-28 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qbank', '0002_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='img',
            name='filetitle',
            field=models.CharField(max_length=200),
        ),
    ]