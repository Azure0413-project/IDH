# Generated by Django 4.2.6 on 2024-03-17 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0025_feedback_empno'),
    ]

    operations = [
        migrations.AddField(
            model_name='warnings',
            name='click_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='warnings',
            name='dismiss_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='warnings',
            name='empNo',
            field=models.CharField(default='--', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='warnings',
            name='warning_DBP',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='warnings',
            name='warning_SBP',
            field=models.DecimalField(decimal_places=3, max_digits=10, null=True),
        ),
    ]
