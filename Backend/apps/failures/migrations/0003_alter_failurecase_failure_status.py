from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("failures", "0002_remove_failurecase_failures_fa_referen_f5a74d_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="failurecase",
            name="failure_status",
            field=models.CharField(
                choices=[
                    ("IN_DEFECT", "In Defect"),
                    ("IN_REPAIR", "In Repair"),
                    ("WAITING_RETEST", "Waiting Retest"),
                    ("REPAIRED", "Repaired"),
                    ("INVALIDATED", "Invalidated"),
                ],
                db_index=True,
                default="IN_DEFECT",
                max_length=30,
            ),
        ),
    ]
