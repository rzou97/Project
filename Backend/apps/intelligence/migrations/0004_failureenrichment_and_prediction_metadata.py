from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("failures", "0003_alter_failurecase_failure_status"),
        ("repairs", "0003_alter_repairticket_ticket_status"),
        ("intelligence", "0003_repairhistory_repair_ticket_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FailureEnrichment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("normalized_family", models.CharField(blank=True, db_index=True, default="", max_length=150)),
                ("normalized_signature", models.CharField(blank=True, db_index=True, default="", max_length=255)),
                ("probable_root_cause", models.TextField(blank=True, default="")),
                ("suggested_action", models.TextField(blank=True, default="")),
                ("suggested_checks", models.JSONField(blank=True, default=list)),
                ("suspect_components", models.JSONField(blank=True, default=list)),
                ("supporting_history_count", models.PositiveIntegerField(default=0)),
                ("confidence_score", models.DecimalField(decimal_places=4, default=0, max_digits=6)),
                ("needs_human_review", models.BooleanField(db_index=True, default=False)),
                (
                    "enrichment_source",
                    models.CharField(
                        choices=[
                            ("RULE", "Rule"),
                            ("HISTORY", "History"),
                            ("ML", "ML"),
                            ("LLM", "LLM"),
                            ("HYBRID", "Hybrid"),
                        ],
                        db_index=True,
                        default="RULE",
                        max_length=20,
                    ),
                ),
                ("model_name", models.CharField(blank=True, default="", max_length=100)),
                ("model_version", models.CharField(blank=True, default="", max_length=30)),
                ("prompt_version", models.CharField(blank=True, default="", max_length=30)),
                ("evidence_json", models.JSONField(blank=True, default=dict)),
                ("enriched_at", models.DateTimeField(db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "failure_case",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="intelligence_enrichment",
                        to="failures.failurecase",
                    ),
                ),
            ],
            options={
                "db_table": "intelligence_failure_enrichment",
                "ordering": ["-enriched_at", "-id"],
                "indexes": [
                    models.Index(fields=["normalized_family"], name="intelligenc_normali_44320c_idx"),
                    models.Index(fields=["normalized_signature"], name="intelligenc_normali_4fa8af_idx"),
                    models.Index(fields=["enrichment_source"], name="intelligenc_enrichm_7196a8_idx"),
                    models.Index(fields=["needs_human_review"], name="intelligenc_needs_h_a8f4e9_idx"),
                    models.Index(fields=["enriched_at"], name="intelligenc_enriche_38f0d5_idx"),
                ],
            },
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="explanation_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="failure_case",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="repair_predictions", to="failures.failurecase"),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="input_signature",
            field=models.CharField(blank=True, db_index=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="model_name",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="model_version",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="prediction_source",
            field=models.CharField(
                choices=[
                    ("RULE", "Rule"),
                    ("HISTORY", "History"),
                    ("ML", "ML"),
                    ("LLM", "LLM"),
                    ("HYBRID", "Hybrid"),
                ],
                db_index=True,
                default="HISTORY",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="repairprediction",
            name="repair_ticket",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="repair_predictions", to="repairs.repairticket"),
        ),
        migrations.AddIndex(
            model_name="repairprediction",
            index=models.Index(fields=["prediction_source"], name="intelligenc_predict_ef9c49_idx"),
        ),
        migrations.AddIndex(
            model_name="repairprediction",
            index=models.Index(fields=["input_signature"], name="intelligenc_input_s_11d2e7_idx"),
        ),
    ]
