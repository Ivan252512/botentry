# Generated by Django 3.1.7 on 2021-07-01 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0005_trade_traceback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='pair',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='individual',
            name='temp',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='trade',
            name='operation',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='trade',
            name='pair',
            field=models.TextField(),
        ),
    ]
