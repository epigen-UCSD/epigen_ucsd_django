# Generated by Django 2.0.4 on 2018-06-08 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nextseq_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinfo',
            name='read_length',
            field=models.CharField(max_length=50),
        ),
    ]