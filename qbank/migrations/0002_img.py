# Generated by Django 4.1 on 2022-11-28 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qbank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Img',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filetitle', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='Img/')),
            ],
        ),
    ]
