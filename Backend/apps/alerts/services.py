from decimal import Decimal
from django.utils import timezone

from apps.alerts.models import AlertEvent, AlertRule
from apps.maintenance.models import CurativeTicket, MaintenanceAsset
from apps.testresults.models import TestResult


def get_or_create_tester_asset(tester_id: str) -> MaintenanceAsset:
    tester_id = (tester_id or "").strip().upper()
    asset, _ = MaintenanceAsset.objects.get_or_create(
        tester_id=tester_id,
        defaults={
            "asset_code": f"TESTER_{tester_id}",
            "asset_name": f"Testeur {tester_id}",
            "asset_type": MaintenanceAsset.AssetType.TESTER,
            "status": MaintenanceAsset.Status.IN_BREAKDOWN,
        },
    )
    return asset


def get_or_create_open_alert(rule: AlertRule, asset: MaintenanceAsset, title: str, description: str):
    alert = (
        AlertEvent.objects.filter(
            rule=rule,
            asset=asset,
            entity_key=asset.tester_id,
            status=AlertEvent.Status.OPEN,
        )
        .order_by("-triggered_at", "-id")
        .first()
    )

    if alert:
        return alert, False

    alert = AlertEvent.objects.create(
        rule=rule,
        asset=asset,
        entity_key=asset.tester_id,
        status=AlertEvent.Status.OPEN,
        title=title,
        description=description,
        severity=rule.severity,
        entity_type="TESTER",
        triggered_at=timezone.now(),
    )
    return alert, True


def get_or_create_open_curative_ticket(rule: AlertRule, asset: MaintenanceAsset, alert_event: AlertEvent, symptom: str):
    ticket = (
        CurativeTicket.objects.filter(
            asset=asset,
            trigger_type=rule.alert_type,
            status__in=[
                CurativeTicket.Status.OPEN,
                CurativeTicket.Status.IN_PROGRESS,
                CurativeTicket.Status.WAITING_VALIDATION,
            ],
        )
        .order_by("-opened_at", "-id")
        .first()
    )

    if ticket:
        return ticket, False

    ticket = CurativeTicket.objects.create(
        asset=asset,
        source_alert_event=alert_event,
        ticket_code=f"{rule.alert_type}_{asset.tester_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
        trigger_type=rule.alert_type,
        title=f"{rule.get_alert_type_display()} - {asset.tester_id}",
        symptom=symptom,
        downtime_start=timezone.now(),
        status=CurativeTicket.Status.OPEN,
        opened_by_system=True,
        opened_at=timezone.now(),
    )
    return ticket, True


def evaluate_repeated_defect_message_rule(rule: AlertRule):
    tester_ids = (
        TestResult.objects.exclude(tester_id="")
        .values_list("tester_id", flat=True)
        .distinct()
    )

    for tester_id in tester_ids:
        last_results = list(
            TestResult.objects.filter(tester_id=tester_id)
            .order_by("-tested_at", "-id")[: rule.consecutive_count]
        )

        if len(last_results) < rule.consecutive_count:
            continue

        same_message = len({(r.failure_message or "").strip() for r in last_results}) == 1
        non_empty_message = (last_results[0].failure_message or "").strip() != ""

        if same_message and non_empty_message:
            asset = get_or_create_tester_asset(tester_id)
            title = f"Défaut répétitif sur {tester_id}"
            description = f"Les {rule.consecutive_count} derniers PV ont le même message de défaut : {last_results[0].failure_message}"
            alert_event, _ = get_or_create_open_alert(rule, asset, title, description)
            get_or_create_open_curative_ticket(rule, asset, alert_event, description)


def evaluate_high_failure_rate_rule(rule: AlertRule):
    since = timezone.now() - timezone.timedelta(minutes=rule.time_window_minutes)

    tester_ids = (
        TestResult.objects.filter(tested_at__gte=since)
        .exclude(tester_id="")
        .values_list("tester_id", flat=True)
        .distinct()
    )

    for tester_id in tester_ids:
        qs = TestResult.objects.filter(tester_id=tester_id, tested_at__gte=since)
        total = qs.count()
        if total == 0:
            continue

        failed = qs.filter(result=TestResult.Result.FAILED).count()
        failure_rate = (Decimal(failed) / Decimal(total)) * Decimal("100")

        if failure_rate > (rule.threshold_value or Decimal("25")):
            asset = get_or_create_tester_asset(tester_id)
            title = f"Taux de panne élevé sur {tester_id}"
            description = f"Failed rate = {failure_rate:.2f}% sur les {rule.time_window_minutes} dernières minutes."
            alert_event, _ = get_or_create_open_alert(rule, asset, title, description)
            get_or_create_open_curative_ticket(rule, asset, alert_event, description)


def evaluate_low_fpy_rule(rule: AlertRule):
    since = timezone.now() - timezone.timedelta(minutes=rule.time_window_minutes)

    tester_ids = (
        TestResult.objects.filter(tested_at__gte=since)
        .exclude(tester_id="")
        .values_list("tester_id", flat=True)
        .distinct()
    )

    for tester_id in tester_ids:
        qs = TestResult.objects.filter(tester_id=tester_id, tested_at__gte=since)
        total = qs.count()
        if total == 0:
            continue

        passed = qs.filter(result=TestResult.Result.PASSED).count()
        fpy = (Decimal(passed) / Decimal(total)) * Decimal("100")

        if fpy < (rule.threshold_value or Decimal("80")):
            asset = get_or_create_tester_asset(tester_id)
            title = f"FPY faible sur {tester_id}"
            description = f"FPY = {fpy:.2f}% sur les {rule.time_window_minutes} dernières minutes."
            alert_event, _ = get_or_create_open_alert(rule, asset, title, description)
            get_or_create_open_curative_ticket(rule, asset, alert_event, description)


def evaluate_active_alert_rules():
    rules = AlertRule.objects.filter(is_active=True)

    for rule in rules:
        if rule.alert_type == AlertRule.AlertType.REPEATED_DEFECT_MESSAGE:
            evaluate_repeated_defect_message_rule(rule)
        elif rule.alert_type == AlertRule.AlertType.HIGH_FAILURE_RATE:
            evaluate_high_failure_rate_rule(rule)
        elif rule.alert_type == AlertRule.AlertType.LOW_FPY:
            evaluate_low_fpy_rule(rule)
