from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("repairs", "0002_repairticket_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="repairticket",
            name="ticket_status",
            field=models.CharField(
                choices=[
                    ("OPEN", "Open"),
                    ("IN_PROGRESS", "In Progress"),
                    ("WAITING_RETEST", "Waiting Retest"),
                    ("CLOSED", "Closed"),
                    ("CANCELLED", "Cancelled"),
                ],
                db_index=True,
                default="OPEN",
                max_length=30,
            ),
        ),
    ]
