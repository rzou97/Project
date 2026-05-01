import re
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.utils import timezone

from apps.failures.models import FailureCase
from apps.repairs.models import RepairTicket

from .models import (
    FailureEnrichment,
    RepairHistory,
    RepairPrediction,
    RepairProcedureTemplate,
)


class FailureIntelligenceService:
    COMPONENT_PATTERN = re.compile(
        r"\b(?:RG|IC|MOS|U|Q|D|ZD|TR|C|R|L|F|CN|J)\d+[A-Z0-9-]*\b",
        re.IGNORECASE,
    )
    TOKEN_PATTERN = re.compile(r"[A-Z0-9]+")
    STOPWORDS = {
        "THE",
        "AND",
        "FOR",
        "WITH",
        "SUR",
        "MESURE",
        "MEASURE",
        "PRIMARY",
        "BOARD",
        "TEST",
        "FAIL",
        "FAILED",
        "PASS",
        "PASSED",
        "ERROR",
        "TERMINATED",
        "PHASE",
        "MODE",
        "VOLTAGE",
    }

    @staticmethod
    def analyze_failure_case_by_id(failure_case_id: int, repair_ticket_id: int | None = None):
        failure_case = (
            FailureCase.objects.select_related("board", "source_test_result")
            .get(pk=failure_case_id)
        )
        repair_ticket = None
        if repair_ticket_id:
            repair_ticket = RepairTicket.objects.filter(pk=repair_ticket_id).first()
        return FailureIntelligenceService.analyze_failure_case(
            failure_case=failure_case,
            repair_ticket=repair_ticket,
        )

    @staticmethod
    def analyze_failure_case(
        failure_case: FailureCase,
        repair_ticket: RepairTicket | None = None,
    ) -> tuple[FailureEnrichment, RepairPrediction]:
        family = FailureIntelligenceService._normalize_family(failure_case.failure_type)
        signature = FailureIntelligenceService._build_signature(
            failure_type=family,
            failure_message=failure_case.failure_message,
            detected_in_phase=failure_case.detected_in_phase,
        )
        scored_histories = FailureIntelligenceService._find_similar_histories(
            failure_case=failure_case,
            family=family,
            signature=signature,
        )
        template = FailureIntelligenceService._resolve_template(
            failure_type=family,
            signature=signature,
        )

        probable_root_cause = FailureIntelligenceService._pick_weighted_text(
            scored_histories=scored_histories,
            field_name="detected_cause",
        )
        suggested_action = FailureIntelligenceService._pick_weighted_text(
            scored_histories=scored_histories,
            field_name="action_taken",
        )

        if not suggested_action and template and template.recommended_steps:
            suggested_action = str(template.recommended_steps[0]).strip()

        suggested_checks = FailureIntelligenceService._build_suggested_checks(
            scored_histories=scored_histories,
            template=template,
        )
        suspect_components = FailureIntelligenceService._extract_components(
            [
                failure_case.failure_message,
                probable_root_cause,
                suggested_action,
                *suggested_checks,
            ]
        )

        confidence = FailureIntelligenceService._estimate_confidence(
            failure_case=failure_case,
            family=family,
            signature=signature,
            scored_histories=scored_histories,
            template=template,
            probable_root_cause=probable_root_cause,
            suggested_action=suggested_action,
        )
        enrichment_source = FailureIntelligenceService._resolve_source(
            scored_histories=scored_histories,
            template=template,
        )
        evidence = FailureIntelligenceService._build_evidence_payload(
            failure_case=failure_case,
            family=family,
            signature=signature,
            scored_histories=scored_histories,
            template=template,
        )
        needs_human_review = (
            confidence < Decimal("0.6000")
            or not probable_root_cause
            or not suggested_action
        )

        enrichment, _ = FailureEnrichment.objects.update_or_create(
            failure_case=failure_case,
            defaults={
                "normalized_family": family,
                "normalized_signature": signature,
                "probable_root_cause": probable_root_cause,
                "suggested_action": suggested_action,
                "suggested_checks": suggested_checks,
                "suspect_components": suspect_components,
                "supporting_history_count": len(scored_histories),
                "confidence_score": confidence,
                "needs_human_review": needs_human_review,
                "enrichment_source": enrichment_source,
                "model_name": FailureIntelligenceService._default_model_name(),
                "model_version": FailureIntelligenceService._default_model_version(),
                "prompt_version": "",
                "evidence_json": evidence,
                "enriched_at": timezone.now(),
            },
        )

        if repair_ticket is None:
            repair_ticket = (
                failure_case.repair_tickets.order_by("-opened_at", "-id").first()
                if hasattr(failure_case, "repair_tickets")
                else None
            )

        prediction = RepairPrediction.objects.create(
            failure_case=failure_case,
            repair_ticket=repair_ticket,
            prediction_type="REPAIR_CAUSE",
            target_serial_number=failure_case.serial_number,
            predicted_cause=probable_root_cause,
            recommended_action=suggested_action,
            recommended_procedure=template,
            prediction_source=enrichment_source,
            model_name=FailureIntelligenceService._default_model_name(),
            model_version=FailureIntelligenceService._default_model_version(),
            input_signature=signature,
            explanation_json={
                "suggested_checks": suggested_checks,
                "suspect_components": suspect_components,
                "supporting_history_ids": [history.id for _, history in scored_histories[:5]],
                "needs_human_review": needs_human_review,
            },
            confidence_score=confidence,
            predicted_at=timezone.now(),
        )

        return enrichment, prediction

    @staticmethod
    def _normalize_family(raw_failure_type: str) -> str:
        value = (raw_failure_type or "").strip().upper()
        return value or "UNKNOWN"

    @staticmethod
    def _build_signature(
        failure_type: str,
        failure_message: str,
        detected_in_phase: str,
    ) -> str:
        chunks = [failure_type or "", failure_message or "", detected_in_phase or ""]
        tokens = []
        for chunk in chunks:
            for token in FailureIntelligenceService.TOKEN_PATTERN.findall((chunk or "").upper()):
                if len(token) <= 1 or token in FailureIntelligenceService.STOPWORDS:
                    continue
                tokens.append(token)

        unique_tokens = []
        seen = set()
        for token in tokens:
            if token in seen:
                continue
            seen.add(token)
            unique_tokens.append(token)

        return " ".join(unique_tokens[:20])[:255]

    @staticmethod
    def _tokenize(value: str) -> set[str]:
        return {
            token
            for token in FailureIntelligenceService.TOKEN_PATTERN.findall((value or "").upper())
            if len(token) > 1 and token not in FailureIntelligenceService.STOPWORDS
        }

    @staticmethod
    def _history_signature(history: RepairHistory) -> str:
        return FailureIntelligenceService._build_signature(
            failure_type=history.failure_type,
            failure_message=history.failure_message,
            detected_in_phase=history.detected_in_phase,
        )

    @staticmethod
    def _find_similar_histories(
        failure_case: FailureCase,
        family: str,
        signature: str,
    ) -> list[tuple[int, RepairHistory]]:
        candidates = list(
            RepairHistory.objects.filter(failure_type__iexact=family)
            .exclude(failure_case_id=failure_case.id)
            .order_by("-created_at", "-id")[:200]
        )

        target_tokens = FailureIntelligenceService._tokenize(signature)
        scored_histories: list[tuple[int, RepairHistory]] = []

        for history in candidates:
            score = 0

            if (
                failure_case.internal_reference
                and history.internal_reference
                and history.internal_reference.upper() == failure_case.internal_reference.upper()
            ):
                score += 4

            if (
                failure_case.client_reference
                and history.client_reference
                and history.client_reference.upper() == failure_case.client_reference.upper()
            ):
                score += 2

            if history.detected_in_phase == failure_case.detected_in_phase:
                score += 2

            if history.detected_on_tester == failure_case.detected_on_tester:
                score += 1

            history_signature = FailureIntelligenceService._history_signature(history)
            if history_signature == signature:
                score += 5
            else:
                overlap = len(
                    target_tokens.intersection(
                        FailureIntelligenceService._tokenize(history_signature)
                    )
                )
                score += min(overlap, 4)

            if (history.final_outcome or "").upper() == "REPAIRED":
                score += 1

            if score > 0:
                scored_histories.append((score, history))

        scored_histories.sort(
            key=lambda item: (
                item[0],
                item[1].created_at,
                item[1].id,
            ),
            reverse=True,
        )
        return scored_histories[:20]

    @staticmethod
    def _pick_weighted_text(
        scored_histories: list[tuple[int, RepairHistory]],
        field_name: str,
    ) -> str:
        weights = Counter()
        for score, history in scored_histories:
            value = (getattr(history, field_name, "") or "").strip()
            if not value:
                continue
            weights[value] += max(score, 1)

        if not weights:
            return ""
        return weights.most_common(1)[0][0]

    @staticmethod
    def _resolve_template(
        failure_type: str,
        signature: str,
    ) -> RepairProcedureTemplate | None:
        exact_template = (
            RepairProcedureTemplate.objects.filter(
                failure_type__iexact=failure_type,
                failure_signature__iexact=signature,
            )
            .order_by("-generated_at", "-id")
            .first()
        )
        if exact_template:
            return exact_template

        return (
            RepairProcedureTemplate.objects.filter(failure_type__iexact=failure_type)
            .order_by("-generated_at", "-id")
            .first()
        )

    @staticmethod
    def _build_suggested_checks(
        scored_histories: list[tuple[int, RepairHistory]],
        template: RepairProcedureTemplate | None,
    ) -> list[str]:
        checks: list[str] = []

        if template and template.recommended_steps:
            for step in template.recommended_steps:
                text = str(step).strip()
                if text and text not in checks:
                    checks.append(text)

        for field_name in ("detected_cause", "action_taken"):
            weights = Counter()
            for score, history in scored_histories:
                value = (getattr(history, field_name, "") or "").strip()
                if not value:
                    continue
                weights[value] += max(score, 1)

            for value, _weight in weights.most_common():
                if value and value not in checks:
                    checks.append(value)
                if len(checks) >= 5:
                    return checks

        return checks[:5]

    @staticmethod
    def _extract_components(texts: list[str]) -> list[str]:
        components: list[str] = []
        seen = set()

        for text in texts:
            for match in FailureIntelligenceService.COMPONENT_PATTERN.findall((text or "").upper()):
                if match in seen:
                    continue
                seen.add(match)
                components.append(match)

        return components[:8]

    @staticmethod
    def _estimate_confidence(
        failure_case: FailureCase,
        family: str,
        signature: str,
        scored_histories: list[tuple[int, RepairHistory]],
        template: RepairProcedureTemplate | None,
        probable_root_cause: str,
        suggested_action: str,
    ) -> Decimal:
        score = Decimal("0.2500")
        if family and family != "UNKNOWN":
            score += Decimal("0.1000")

        if signature:
            score += Decimal("0.0500")

        if scored_histories:
            score += Decimal("0.2000")

        if any(
            history.internal_reference.upper() == failure_case.internal_reference.upper()
            for _, history in scored_histories
            if failure_case.internal_reference and history.internal_reference
        ):
            score += Decimal("0.1500")

        if any(
            FailureIntelligenceService._history_signature(history) == signature
            for _, history in scored_histories
        ):
            score += Decimal("0.1500")

        if probable_root_cause:
            score += Decimal("0.1000")

        if suggested_action:
            score += Decimal("0.1000")

        if template is not None:
            score += Decimal("0.1000")

        if len(scored_histories) >= 5:
            score += Decimal("0.0500")

        return min(score, Decimal("0.9900")).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _resolve_source(
        scored_histories: list[tuple[int, RepairHistory]],
        template: RepairProcedureTemplate | None,
    ) -> str:
        if scored_histories and template:
            return FailureEnrichment.Source.HYBRID
        if scored_histories:
            return FailureEnrichment.Source.HISTORY
        return FailureEnrichment.Source.RULE

    @staticmethod
    def _build_evidence_payload(
        failure_case: FailureCase,
        family: str,
        signature: str,
        scored_histories: list[tuple[int, RepairHistory]],
        template: RepairProcedureTemplate | None,
    ) -> dict:
        exact_signature_matches = sum(
            1
            for _, history in scored_histories
            if FailureIntelligenceService._history_signature(history) == signature
        )

        return {
            "failure_case_id": failure_case.id,
            "normalized_family": family,
            "normalized_signature": signature,
            "supporting_history_ids": [history.id for _, history in scored_histories[:10]],
            "supporting_history_scores": [
                {"id": history.id, "score": score}
                for score, history in scored_histories[:10]
            ],
            "supporting_history_count": len(scored_histories),
            "exact_signature_matches": exact_signature_matches,
            "template_id": template.id if template else None,
        }

    @staticmethod
    def _default_model_name() -> str:
        return getattr(settings, "INTELLIGENCE_DEFAULT_MODEL_NAME", "history-rules")

    @staticmethod
    def _default_model_version() -> str:
        return getattr(settings, "INTELLIGENCE_DEFAULT_MODEL_VERSION", "v1")


class AiRepairAdvisor:
    @staticmethod
    def buildRepairProcedure(failure_type: str, failure_signature: str = ""):
        return AiRepairAdvisor.build_repair_procedure(
            failure_type=failure_type,
            failure_signature=failure_signature,
        )

    @staticmethod
    def predictRepair(failure_case: FailureCase, repair_ticket: RepairTicket | None = None):
        return AiRepairAdvisor.predict_repair(
            failure_case=failure_case,
            repair_ticket=repair_ticket,
        )

    @staticmethod
    def scoreRepairEffectiveness(repair_ticket: RepairTicket):
        return AiRepairAdvisor.score_repair_effectiveness(repair_ticket=repair_ticket)

    @staticmethod
    def suggestParts(failure_type: str):
        return AiRepairAdvisor.suggest_parts(failure_type=failure_type)

    @staticmethod
    def build_repair_procedure(failure_type: str, failure_signature: str = "") -> RepairProcedureTemplate:
        histories = RepairHistory.objects.filter(failure_type__iexact=failure_type)
        if failure_signature:
            histories = histories.filter(failure_message__icontains=failure_signature)

        actions = list(
            histories.exclude(action_taken="")
            .values_list("action_taken", flat=True)
            .distinct()[:5]
        )
        causes = list(
            histories.exclude(detected_cause="")
            .values_list("detected_cause", flat=True)
            .distinct()[:5]
        )

        total = histories.count()
        repaired = histories.filter(final_outcome__iexact="REPAIRED").count()
        success_rate = Decimal("0.00")
        if total > 0:
            success_rate = (Decimal(repaired) / Decimal(total)) * Decimal("100")

        existing_versions = RepairProcedureTemplate.objects.filter(
            failure_type__iexact=failure_type
        ).count()
        version = f"v{existing_versions + 1}"

        return RepairProcedureTemplate.objects.create(
            procedure_name=f"PROC_{failure_type}_{version}",
            failure_type=failure_type,
            failure_signature=failure_signature or "",
            recommended_steps=actions if actions else causes,
            recommended_parts=[],
            success_rate=success_rate.quantize(Decimal("0.01")),
            version=version,
            generated_at=timezone.now(),
        )

    @staticmethod
    def predict_repair(
        failure_case: FailureCase,
        repair_ticket: RepairTicket | None = None,
    ) -> RepairPrediction:
        _enrichment, prediction = FailureIntelligenceService.analyze_failure_case(
            failure_case=failure_case,
            repair_ticket=repair_ticket,
        )
        return prediction

    @staticmethod
    def score_repair_effectiveness(repair_ticket: RepairTicket) -> Decimal:
        latest_history = (
            RepairHistory.objects.filter(repair_ticket=repair_ticket)
            .order_by("-created_at", "-id")
            .first()
        )

        score = Decimal("50.00")
        if latest_history:
            if latest_history.final_outcome.upper() == "REPAIRED":
                score = Decimal("100.00")
            elif latest_history.final_outcome.upper() == "WAITING_RETEST":
                score = Decimal("75.00")
            elif latest_history.final_outcome.upper() == "IN_PROGRESS":
                score = Decimal("50.00")

        repair_ticket.repair_effectiveness = score
        repair_ticket.save(update_fields=["repair_effectiveness", "updated_at"])
        return score

    @staticmethod
    def suggest_parts(failure_type: str) -> list:
        template = (
            RepairProcedureTemplate.objects.filter(failure_type__iexact=failure_type)
            .exclude(recommended_parts=[])
            .order_by("-generated_at", "-id")
            .first()
        )
        if not template:
            return []
        return template.recommended_parts
