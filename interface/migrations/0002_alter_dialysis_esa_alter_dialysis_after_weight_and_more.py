# Generated by Django 4.1.3 on 2022-11-07 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interface", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dialysis",
            name="ESA",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="after_weight",
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="before_weight",
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="conductivity",
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="ideal_weight",
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="real_dehydration",
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="start_temperature",
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="temperature",
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name="record", name="flush", field=models.IntegerField(null=True),
        ),
    ]
