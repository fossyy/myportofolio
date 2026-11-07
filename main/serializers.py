from django.utils.html import strip_tags
from rest_framework import serializers

from experiences.models import Experience


class ExperienceSerializer(serializers.ModelSerializer):
    category_display = serializers.ReadOnlyField(source="get_category_display")
    period = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

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
        return self._clean_required_text(value, "Role / title can't contain only HTML tags.")

    def validate_organization(self, value):
        return self._clean_required_text(value, "Organization can't contain only HTML tags.")

    def validate_description(self, value):
        return self._clean_required_text(value, "Description cannot be empty.")

    def validate_project(self, value):
        return strip_tags(value).strip()

    def validate_technologies(self, value):
        return strip_tags(value).strip()

    def _clean_required_text(self, value, message):
        cleaned = strip_tags(value).strip()
        if not cleaned:
            raise serializers.ValidationError(message)
        return cleaned

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())
