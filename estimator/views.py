from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from estimator.serializers import *
from estimator.services import phase, project, customer, estimate
from .models import *


class ArchestAuthenticatedModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)


class CustomerViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Customers to be viewed or edited.
    """

    queryset = Customer.objects.none()

    def get_queryset(self):
        return customer.get_records(self.request)

    serializer_class = CustomerSerializer


class ProjectViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Projects to be viewed or edited.
    """

    queryset = Project.objects.none()

    def get_queryset(self):
        return project.get_records(self.request)

    serializer_class = ProjectSerializer


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


class EstimateViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Estimates to be viewed or edited.
    """

    queryset = Estimate.objects.none()
    serializer_class = EstimateSerializer

    def get_queryset(self):
        return estimate.get_records(self.request)

    @action(detail=True, methods=['get'])
    def detailed_read_view(self, request, pk=None):
        activity_serializer = ActivitySerializer(Activity.objects.filter(estimate=pk), many=True)
        return Response({"results": activity_serializer.data})
