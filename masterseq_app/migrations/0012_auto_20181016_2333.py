# Generated by Django 2.0.6 on 2018-10-17 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterseq_app', '0011_auto_20181016_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sampleinfo',
            name='preparation',
            field=models.CharField(choices=[('flash frozen without cryopreservant', 'flash frozen without cryopreservant'), ('flash frozen with cryopreservant', 'flash frozen with cryopreservant'), ('slow frozen with cryopreservant', 'slow frozen with cryopreservant'), ('fresh', 'fresh'), ('other', 'other')], max_length=50),
        ),
    ]
