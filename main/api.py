import json

from django.core import serializers


def serialize_section(queryset, section_model, fields=None):
    """Keep the pre-split JSON model label stable for existing API clients."""
    payload = serializers.serialize("json", queryset, fields=fields)
    records = json.loads(payload)
    for record in records:
        record["model"] = f"main.{section_model}"
    return json.dumps(records)
