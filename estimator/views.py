from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from estimator.serializers import *
from estimator.services import phase, project, customer, estimate, activity, subactivity, work_entries
from .models import *


class ArchestAuthenticatedModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)


"""
TODO: IMPORTANT!!!!!!!!!! --------- For All CRUD operations check authenticate and authorize the requests. ------------- 
"""


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

    def create(self, request, *args, **kwargs):
        logged_in_user = User.objects.filter(username=request.user).first()  # type:User
        phase_added_to = Phase.objects.filter(id=request.data['phase_id']).first()  # type:Phase
        estimate_object = Estimate.objects.create(
            owner_id=logged_in_user.resource.id,
            name=phase_added_to.name + ' ' + ' - Estimate by ' + logged_in_user.first_name,
            phase_id=request.data['phase_id'],
        )  # type:Estimate
        estimate_serializer = self.get_serializer(estimate_object, data=request.data, partial=True)
        estimate_serializer.is_valid(raise_exception=True)
        estimate_serializer.save()
        return Response(estimate_serializer.data)

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
        activity_object = Activity.objects.create(
            feature_id=request.data['feature_id'],
            name=request.data['name'],
            estimate_id=request.data['estimate_id'],
            estimated_time=request.data['estimated_time'],
            status=request.data['status']
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
            status=request.data['status'],
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


class ActivityWorkEntriesViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Activity Work Entries to be viewed or edited.
    """

    queryset = ActivityWorkEntry.objects.none()

    def get_queryset(self):
        return work_entries.get_activity_work_entries(self.request)

    serializer_class = ActivityWorkEntrySerializer

    def create(self, request, *args, **kwargs):
        activity_we_object = ActivityWorkEntry.objects.create(
            activity_id=request.data['activity_id'],
            worked_hours=request.data['worked_hours'],
            date=request.data['date'],
            note=request.data['note'],
        )  # type:ActivityWorkEntry
        activity_we_serializer = self.get_serializer(activity_we_object, data=request.data, partial=True)
        activity_we_serializer.is_valid(raise_exception=True)
        activity_we_serializer.save()
        return Response(activity_we_serializer.data)


class SubActivityWorkEntriesViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows SubActivity Work Entries to be viewed or edited.
    """

    queryset = SubActivityWorkEntry.objects.none()

    def get_queryset(self):
        return work_entries.get_sub_activity_work_entries(self.request)

    serializer_class = SubActivityWorkEntrySerializer

    def create(self, request, *args, **kwargs):
        sub_activity_we_object = SubActivityWorkEntry.objects.create(
            sub_activity_id=request.data['sub_activity_id'],
            worked_hours=request.data['worked_hours'],
            date=request.data['date'],
            note=request.data['note'],
        )  # type:SubActivityWorkEntry
        sub_activity_we_serializer = self.get_serializer(sub_activity_we_object, data=request.data, partial=True)
        sub_activity_we_serializer.is_valid(raise_exception=True)
        sub_activity_we_serializer.save()
        return Response(sub_activity_we_serializer.data)
