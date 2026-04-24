from rest_framework import serializers

from apps.syncengine.models import SyncCursor


class SyncCursorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncCursor
        fields = (
            "id",
            "source_table",
            "last_source_id",
            "last_source_timestamp",
            "sync_status",
            "last_synced_at",
            "rows_processed",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SyncRunRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=5000, default=500)


class SyncRunResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    state = serializers.CharField()
    queued_at = serializers.DateTimeField()
    limit = serializers.IntegerField()


class SyncTaskStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    state = serializers.CharField()
    ready = serializers.BooleanField()
    successful = serializers.BooleanField()
    failed = serializers.BooleanField()
    result = serializers.JSONField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_blank=True)
