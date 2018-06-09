# Generated by Django 2.0.4 on 2018-06-07 22:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indexid', models.CharField(max_length=200, unique=True)),
                ('indexseq', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['indexid'],
            },
        ),
        migrations.CreateModel(
            name='RunInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Flowcell_ID', models.CharField(help_text='Please enter the FlowcellSerialNumber, like H5GLYBGX5', max_length=200, unique=True)),
                ('date', models.DateField(blank=True, help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', null=True, verbose_name='I did this run on...')),
                ('read_type', models.CharField(choices=[('SE', 'Single-end'), ('PE', 'Paired-end')], max_length=2)),
                ('read_length', models.IntegerField()),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SamplesInRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Library_ID', models.CharField(max_length=200, unique=True)),
                ('i5index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='i5_index', to='nextseq_app.Barcode')),
                ('i7index', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='i7_index', to='nextseq_app.Barcode')),
                ('singlerun', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nextseq_app.RunInfo')),
            ],
            options={
                'ordering': ['Library_ID'],
            },
        ),
    ]