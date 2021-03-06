# Generated by Django 3.1.4 on 2022-06-13 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esr21_reports', '0005_auto_20220613_2124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vaccinationstatistics',
            name='dose_1',
        ),
        migrations.RemoveField(
            model_name='vaccinationstatistics',
            name='dose_2',
        ),
        migrations.RemoveField(
            model_name='vaccinationstatistics',
            name='dose_3',
        ),
        migrations.AddField(
            model_name='vaccinationstatistics',
            name='dose_1_percent',
            field=models.FloatField(default=0, verbose_name='First Dose'),
        ),
        migrations.AddField(
            model_name='vaccinationstatistics',
            name='dose_2_percent',
            field=models.FloatField(default=0, verbose_name='Second Dose'),
        ),
        migrations.AddField(
            model_name='vaccinationstatistics',
            name='dose_3_percent',
            field=models.FloatField(default=0, verbose_name='Booster Dose'),
        ),
    ]
