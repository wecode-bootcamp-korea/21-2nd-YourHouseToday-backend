# Generated by Django 3.2.4 on 2021-06-23 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='kakao_id',
            field=models.CharField(default='', max_length=20),
        ),
    ]