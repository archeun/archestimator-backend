from rest_framework.decorators import action
from rest_framework.response import Response

from estimator.models import Project
from estimator.serializers import PhaseSerializer, ProjectSerializer
from estimator.services import project
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


class ProjectViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Projects to be viewed or edited.
    """

    queryset = Project.objects.none()

    def get_queryset(self):
        return project.get_records(self.request)

    @action(detail=True, methods=['get'])
    def phases(self, request, pk=None):
        phase_serializer = PhaseSerializer(project.get_phases(request, pk), many=True)
        return Response({"results": phase_serializer.data})

    serializer_class = ProjectSerializer
