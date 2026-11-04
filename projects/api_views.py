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

from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from projects.models import Project
from projects.serializers import ProjectSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        title_query = strip_tags(request.query_params.get("title", "")).strip()
        projects = Project.objects.prefetch_related("starred_by").all()
        if title_query:
            projects = projects.filter(title__icontains=title_query)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("starred_by"), pk=pk)

    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)
    if request.method in ("PUT", "PATCH"):
        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    project.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("starred_by"), pk=pk)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    project.refresh_from_db()
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)
