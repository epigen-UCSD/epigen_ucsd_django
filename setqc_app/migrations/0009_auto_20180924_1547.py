# Generated by Django 2.0.6 on 2018-09-24 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setqc_app', '0008_auto_20180918_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='librariessetqc',
            name='report_status',
            field=models.CharField(blank=True, default='ClickToSubmit', max_length=200),
        ),
        migrations.AddField(
            model_name='librariessetqc',
            name='version',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
