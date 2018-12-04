# Generated by Django 2.0.6 on 2018-10-16 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterseq_app', '0009_auto_20181016_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='sampleinfo',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='libraryinfo',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='protocalinfo',
            name='experiment_type',
            field=models.CharField(choices=[('ATAC-seq', 'ATAC-seq'), ('ChIP-seq', 'ChIP-seq'), ('Hi-C Arima Kit', 'Hi-C Arima Kit'), ('Hi-C Epigen', 'Hi-C Epigen'), ('scATAC-seq', 'scATAC-seq'), ('scRNA-seq', 'scRNA-seq'), ('snRNA-seq', 'snRNA-seq'), ('4C', '4C'), ('CUT&RUN', 'CUT&RUN'), ('Other', 'Other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='sampleinfo',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='sampleinfo',
            name='preparation',
            field=models.CharField(choices=[('FACS sorted cells', 'FACS sorted cells'), ('douncing homogenization', 'douncing homogenization'), ('flash frozen', 'flash frozen'), ('flash frozen with cryopreservant', 'flash frozen with cryopreservant'), ('slow frozen with cryopreservant', 'slow frozen with cryopreservant'), ('other', 'other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='sampleinfo',
            name='sample_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sampleinfo',
            name='sample_type',
            field=models.CharField(choices=[('cultured cells', 'cultured cells'), ('isolated cells', 'isolated cells'), ('isolated nuclei', 'isolated nuclei'), ('PcA cell line', 'PcA cell line'), ('tissue', 'tissue'), ('other', 'other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='sampleinfo',
            name='species',
            field=models.CharField(choices=[('human', 'human'), ('mouse', 'mouse'), ('other', 'other')], max_length=10),
        ),
    ]