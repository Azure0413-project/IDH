# Generated by Django 4.2.6 on 2023-12-14 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0018_alter_predict_pred_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='predict',
            name='flag',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]