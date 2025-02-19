# Generated by Django 4.2.6 on 2024-05-21 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0027_dialysis_random_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='drug_all',
            field=models.CharField(default='--', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='inject_all',
            field=models.CharField(default='--', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='is_nursing',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='nursing_all',
            field=models.CharField(default='--', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='other_all',
            field=models.CharField(default='--', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='setting_all',
            field=models.CharField(default='--', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dialysis',
            name='random_code',
            field=models.IntegerField(default=1),
        ),
    ]
