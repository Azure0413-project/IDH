# Generated by Django 4.1.3 on 2022-12-28 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("interface", "0011_remove_feedback_is_noise_remove_feedback_r_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="d_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="interface.dialysis",
            ),
            preserve_default=False,
        ),
    ]
