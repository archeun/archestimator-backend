from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from estimator.serializers import *
from estimator.services import phase, project, customer, estimate, activity, subactivity
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

    def create(self, request, *args, **kwargs):
        print(request.data)
        activity_object = Activity.objects.create(
            feature_id=request.data['feature_id'],
            name=request.data['name'],
            estimate_id=request.data['estimate_id'],
            estimated_time=request.data['estimated_time'],
            is_completed=request.data['is_completed']
        )  # type:Activity
        activity_serializer = self.get_serializer(activity_object, data=request.data, partial=True)
        activity_serializer.is_valid(raise_exception=True)
        activity_serializer.save()
        return Response(activity_serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)

        activity_obj = self.get_object()  # type:Activity
        activity_obj.feature_id = request.data['feature_id']
        activity_serializer = self.get_serializer(activity_obj, data=request.data, partial=partial)
        activity_serializer.is_valid(raise_exception=True)
        activity_serializer.save()
        return Response(activity_serializer.data)


class SubActivityViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows SubActivities to be viewed or edited.
    """

    queryset = SubActivity.objects.none()
    serializer_class = SubActivitySerializer

    def get_queryset(self):
        return subactivity.get_records(self.request)

    def create(self, request, *args, **kwargs):
        sub_activity_object = SubActivity.objects.create(
            parent_id=request.data['parent_id'],
            name=request.data['name'],
            estimated_time=request.data['estimated_time'],
            is_completed=False
        )  # type:SubActivity
        sub_activity_serializer = self.get_serializer(sub_activity_object, data=request.data)
        sub_activity_serializer.is_valid(raise_exception=True)
        sub_activity_serializer.save()
        return Response(sub_activity_serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)
        sub_activity_object = self.get_object()  # type:SubActivity
        sub_activity_serializer = self.get_serializer(sub_activity_object, data=request.data, partial=partial)
        sub_activity_serializer.is_valid(raise_exception=True)
        sub_activity_serializer.save()
        return Response(sub_activity_serializer.data)
