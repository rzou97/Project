from celery import shared_task

from apps.alerts.models import AlertRule
from apps.alerts.services import evaluate_active_alert_rules


@shared_task
def evaluate_alert_rules_task():
    active_rule_count = AlertRule.objects.filter(is_active=True).count()
    evaluate_active_alert_rules()

    return {
        "status": "success",
        "active_rule_count": active_rule_count,
    }
