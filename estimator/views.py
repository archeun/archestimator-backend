from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from estimator.serializers import *
from estimator.services import phase, project, customer, estimate, activity
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
    def detailed_view(self, request, pk=None):
        """
        Returns the Estimate along with its activities, sub activities
        :param request:
        :param pk:
        :return:
        """
        activity_serializer = ActivitySerializer(Activity.objects.filter(estimate=pk), many=True)
        return Response({"results": activity_serializer.data})


class ActivityViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Activities to be viewed or edited.
    """

    queryset = Activity.objects.none()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        return activity.get_records(self.request)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)

        instance = self.get_object()  # type:Activity
        instance.feature_id = request.data['feature_id']
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
