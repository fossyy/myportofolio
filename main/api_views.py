from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from experiences.models import Experience
from main.serializers import ExperienceSerializer
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        title_query = strip_tags(request.query_params.get("title", "")).strip()
        experiences = Experience.objects.prefetch_related("starred_by").all()
        if title_query:
            experiences = experiences.filter(title__icontains=title_query)
        serializer = ExperienceSerializer(
            experiences, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, pk):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"), pk=pk
    )

    if request.method in ("GET", "HEAD"):
        serializer = ExperienceSerializer(experience, context={"request": request})
        return Response(serializer.data)
    if request.method in ("PUT", "PATCH"):
        serializer = ExperienceSerializer(
            experience,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    experience.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, pk):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"), pk=pk
    )
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    experience.refresh_from_db()
    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)
