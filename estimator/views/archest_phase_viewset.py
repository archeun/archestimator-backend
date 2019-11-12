from rest_framework.decorators import action
from rest_framework.response import Response

from estimator.models import Phase
from estimator.serializers import PhaseSerializer, EstimateSerializer, ResourceSerializer
from estimator.services import phase
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


class PhaseViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Phases to be viewed or edited.
    """

    queryset = Phase.objects.none()
    serializer_class = PhaseSerializer

    def get_queryset(self):
        return phase.get_records(self.request)

    @action(detail=True, methods=['get'])
    def estimates(self, request, pk=None):
        estimate_serializer = EstimateSerializer(phase.get_estimates(request, pk), many=True)
        return Response({"results": estimate_serializer.data})

    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        resource_serializer = ResourceSerializer(phase.get_resources(request, pk), many=True)
        return Response({"results": resource_serializer.data})

    def create(self, request, *args, **kwargs):
        phase_object = Phase.objects.create(
            project_id=request.data['project_id'],
            name=request.data['name'],
        )  # type:Phase
        phase_serializer = self.get_serializer(phase_object, data=request.data, partial=True)
        phase_serializer.is_valid(raise_exception=True)
        phase_serializer.save()
        return Response(phase_serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)

        phase_obj = self.get_object()  # type:Phase
        print(request.data)
        activity_serializer = self.get_serializer(phase_obj, data=request.data, partial=partial)
        activity_serializer.is_valid(raise_exception=True)
        activity_serializer.save()
        return Response(activity_serializer.data)
