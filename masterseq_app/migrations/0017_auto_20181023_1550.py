# Generated by Django 2.0.6 on 2018-10-23 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterseq_app', '0016_auto_20181023_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryinfo',
            name='library_id',
            field=models.CharField(max_length=100),
        ),
    ]