# Generated by Django 2.0.6 on 2018-10-29 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setqc_app', '0021_auto_20181016_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryinset',
            name='label',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
