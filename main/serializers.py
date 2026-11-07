from django.utils.html import strip_tags
from rest_framework import serializers

from experiences.models import Experience
from skills.models import Skill


def _clean_required_text(value, message):
    """Strip markup and reject values that are empty once cleaned."""
    cleaned = strip_tags(value).strip()
    if not cleaned:
        raise serializers.ValidationError(message)
    return cleaned


class StarSerializerMixin(serializers.Serializer):
    """Computed star fields shared by the serializers of starable sections."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(StarSerializerMixin, serializers.ModelSerializer):
    category_display = serializers.ReadOnlyField(source="get_category_display")
    period = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "organization",
            "description",
            "project",
            "technologies",
            "category",
            "category_display",
            "thumbnail",
            "started_at",
            "ended_at",
            "period",
            "is_ongoing",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = [
            "id",
            "category_display",
            "period",
            "is_ongoing",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]

    def validate_title(self, value):
        return _clean_required_text(value, "Role / title can't contain only HTML tags.")

    def validate_organization(self, value):
        return _clean_required_text(value, "Organization can't contain only HTML tags.")

    def validate_description(self, value):
        return _clean_required_text(value, "Description cannot be empty.")

    def validate_project(self, value):
        return strip_tags(value).strip()

    def validate_technologies(self, value):
        return strip_tags(value).strip()


class SkillSerializer(StarSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "category",
            "position",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id", "star_count", "is_starred", "starred_by_names"]

    def validate_name(self, value):
        return _clean_required_text(value, "Skill name can't contain only HTML tags.")

    def validate_category(self, value):
        return _clean_required_text(value, "Category can't contain only HTML tags.")

    def validate_position(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Position cannot be negative.")
        return value
