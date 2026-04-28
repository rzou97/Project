from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.boards.models import Board
from apps.kpi.services import get_current_failure_rate_by_reference


class CurrentFailureRateKpiTests(TestCase):
    def test_counts_current_physical_failures_by_internal_reference(self):
        now = timezone.now()

        Board.objects.create(
            serial_number="SN-001",
            client_reference="REF-1",
            internal_reference="INT-A",
            current_status=Board.Status.IN_DEFECT,
            first_seen_at=now,
            last_seen_at=now,
        )
        Board.objects.create(
            serial_number="SN-002",
            client_reference="REF-1",
            internal_reference="INT-A",
            current_status=Board.Status.HEALTHY,
            first_seen_at=now,
            last_seen_at=now,
        )
        Board.objects.create(
            serial_number="SN-003",
            client_reference="REF-2",
            internal_reference="INT-B",
            current_status=Board.Status.WAITING_RETEST,
            first_seen_at=now,
            last_seen_at=now,
        )
        Board.objects.create(
            serial_number="SN-004",
            client_reference="REF-2",
            internal_reference="INT-B",
            current_status=Board.Status.REPAIRED,
            first_seen_at=now,
            last_seen_at=now,
        )

        payload = get_current_failure_rate_by_reference()

        self.assertEqual(payload["total_sn"], 4)
        self.assertEqual(payload["total_defective_sn"], 2)
        self.assertEqual(payload["current_failure_rate"], Decimal("50.00"))

        by_reference = {
            item["internal_reference"]: item for item in payload["references"]
        }

        self.assertEqual(by_reference["INT-A"]["total_sn"], 2)
        self.assertEqual(by_reference["INT-A"]["defective_sn"], 1)
        self.assertEqual(by_reference["INT-A"]["current_failure_rate"], Decimal("50.00"))

        self.assertEqual(by_reference["INT-B"]["total_sn"], 2)
        self.assertEqual(by_reference["INT-B"]["defective_sn"], 1)
        self.assertEqual(by_reference["INT-B"]["current_failure_rate"], Decimal("50.00"))

    def test_repaired_board_is_not_counted_as_current_failure(self):
        now = timezone.now()

        Board.objects.create(
            serial_number="SN-005",
            client_reference="REF-3",
            internal_reference="INT-C",
            current_status=Board.Status.REPAIRED,
            first_seen_at=now,
            last_seen_at=now,
        )

        payload = get_current_failure_rate_by_reference()

        self.assertEqual(payload["total_sn"], 1)
        self.assertEqual(payload["total_defective_sn"], 0)
        self.assertEqual(payload["current_failure_rate"], Decimal("0.00"))
