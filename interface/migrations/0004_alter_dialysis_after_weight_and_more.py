# Generated by Django 4.1.3 on 2022-11-07 08:11

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interface", "0003_alter_dialysis_estimate_dehydration_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dialysis",
            name="after_weight",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="before_weight",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="conductivity",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.0"), max_digits=4, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="estimate_dehydration",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="expect_dehydration",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="food",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="ideal_weight",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="real_dehydration",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="set_dehydration",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="start_temperature",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.0"), max_digits=4, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="temperature",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.0"), max_digits=4, null=True
            ),
        ),
        migrations.AlterField(
            model_name="dialysis",
            name="transfusion",
            field=models.DecimalField(
                decimal_places=3, default=Decimal("0.0"), max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="flush",
            field=models.IntegerField(default=Decimal("0.0"), null=True),
        ),
    ]