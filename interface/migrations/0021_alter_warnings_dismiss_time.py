# Generated by Django 4.2.6 on 2023-12-29 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0020_warnings_p_bed_warnings_p_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warnings',
            name='dismiss_time',
            field=models.DateTimeField(),
        ),
    ]