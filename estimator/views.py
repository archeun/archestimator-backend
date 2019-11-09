from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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

    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        resource_serializer = ResourceSerializer(phase.get_resources(request, pk), many=True)
        return Response({"results": resource_serializer.data})


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

        estimate_resource = EstimateResource.objects.create(
            resource_id=logged_in_user.resource.id,
            estimate_id=estimate_object.id,
            access_level=2
        )
        estimate_object.estimateresource_set.add(estimate_resource)
        return Response(estimate_serializer.data)

    @action(detail=True, methods=['get'])
    def detailed_view(self, request, pk=None):
        """
        Returns the Estimate along with its activities, sub activities
        :param request:
        :param pk:
        :return:
        """
        activity_serializer = ActivitySerializer(
            Activity.objects.filter(estimate=pk),
            many=True,
            context={
                'request': request
            })
        return Response({"results": activity_serializer.data})

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Returns the Progress of the Activities/Sub Activities of the Estimate
        :param request:
        :param pk:
        :return:
        """
        # TODO: Check whether the requested estimate is accessible by the logged in user
        return Response({"results": estimate.get_progress(pk)})

    @action(detail=True, methods=['get'])
    def shared_resources(self, request, pk=None):
        """
        Returns the Resources the Estimate is shared with
        :param request:
        :param pk:
        :return:
        """
        # TODO: Check whether the requested estimate is accessible by the logged in user
        estimate_obj = self.get_object()  # type: Estimate

        estimate_resources_serializer = EstimateResourceSerializer(
            estimate.get_shared_resources(estimate_obj, request.user.username), many=True
        )
        return Response({"results": estimate_resources_serializer.data})

    @shared_resources.mapping.patch
    def update_shared_resources(self, request, pk=None):
        """
        Updates the Resources the Estimate is shared with
        :param request:
        :param pk:
        :return:
        """
        # TODO: Check whether the requested estimate is accessible by the logged in user
        estimate.update_shared_resources(self.get_object(), request.data)
        return Response({"results": {}})


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
        if 'feature_id' in request.data:
            activity_obj.feature_id = request.data['feature_id']

        if 'owner_id' in request.data:
            if not request.data['owner_id']:
                activity_obj.owner_id = None
            else:
                activity_obj.owner_id = request.data['owner_id']

        activity_serializer = self.get_serializer(activity_obj, data=request.data, partial=partial)
        activity_serializer.is_valid(raise_exception=True)
        activity_serializer.save()
        return Response(activity_serializer.data)

    @action(detail=True, methods=['get'])
    def work_entries(self, request, pk=None):
        """
        Returns the Work Entries logged against the Activity
        :param request:
        :param pk:
        :return:
        """
        # TODO: Check whether the requested Activity is accessible by the logged in user
        activity_obj = self.get_object()  # type: Activity

        activity_work_entry_serializer = ActivityWorkEntrySerializer(
            activity_obj.activityworkentry_set.all(),
            many=True,
            context={
                'request': request
            }
        )
        activity_data = self.get_serializer(activity_obj).data
        return Response({"results": {'work_entries': activity_work_entry_serializer.data, 'activity': activity_data}})


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
        sub_activity_serializer = self.get_serializer(sub_activity_object, data=request.data, partial=True)
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

        if 'owner_id' in request.data:
            if not request.data['owner_id']:
                sub_activity_object.owner_id = None
            else:
                sub_activity_object.owner_id = request.data['owner_id']
        sub_activity_serializer = self.get_serializer(sub_activity_object, data=request.data, partial=partial)
        sub_activity_serializer.is_valid(raise_exception=True)
        sub_activity_serializer.save()
        return Response(sub_activity_serializer.data)

    @action(detail=True, methods=['get'])
    def work_entries(self, request, pk=None):
        """
        Returns the Work Entries logged against the SubActivity
        :param request:
        :param pk:
        :return:
        """
        # TODO: Check whether the requested SubActivity is accessible by the logged in user
        sub_activity_obj = self.get_object()  # type: SubActivity

        sub_activity_work_entry_serializer = SubActivityWorkEntrySerializer(
            sub_activity_obj.subactivityworkentry_set.all(),
            many=True,
            context={
                'request': request
            }
        )
        sub_activity_data = self.get_serializer(sub_activity_obj).data
        return Response(
            {"results": {'work_entries': sub_activity_work_entry_serializer.data, 'sub_activity': sub_activity_data}})


class ActivityWorkEntriesViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Activity Work Entries to be viewed or edited.
    """

    pagination_class = None
    queryset = ActivityWorkEntry.objects.none()
    serializer_class = ActivityWorkEntrySerializer

    def get_queryset(self):
        return work_entries.get_activity_work_entries(self.request)

    def create(self, request, *args, **kwargs):
        activity_we_object = ActivityWorkEntry.objects.create(
            activity_id=request.data['activity_id'],
            worked_hours=request.data['worked_hours'],
            date=request.data['date'],
            note=request.data['note'],
            owner_id=Resource.objects.filter(user__username=request.user).get().id
        )  # type:ActivityWorkEntry
        activity_we_serializer = self.get_serializer(activity_we_object, data=request.data, partial=True)
        activity_we_serializer.is_valid(raise_exception=True)
        activity_we_serializer.save()
        return Response(activity_we_serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        partial = kwargs.pop('partial', False)
        activity_we_object = self.get_object()  # type:ActivityWorkEntry
        activity_we_object.activity_id = request.data['activity_id']
        activity_we_serializer = self.get_serializer(activity_we_object, data=request.data, partial=partial)
        activity_we_serializer.is_valid(raise_exception=True)
        activity_we_serializer.save()
        return Response(activity_we_serializer.data)


class SubActivityWorkEntriesViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows SubActivity Work Entries to be viewed or edited.
    """
    pagination_class = None
    queryset = SubActivityWorkEntry.objects.none()
    serializer_class = SubActivityWorkEntrySerializer

    def get_queryset(self):
        return work_entries.get_sub_activity_work_entries(self.request)

    def create(self, request, *args, **kwargs):
        sub_activity_we_object = SubActivityWorkEntry.objects.create(
            sub_activity_id=request.data['sub_activity_id'],
            worked_hours=request.data['worked_hours'],
            date=request.data['date'],
            note=request.data['note'],
            owner_id=Resource.objects.filter(user__username=request.user).get().id
        )  # type:SubActivityWorkEntry
        sub_activity_we_serializer = self.get_serializer(sub_activity_we_object, data=request.data, partial=True)
        sub_activity_we_serializer.is_valid(raise_exception=True)
        sub_activity_we_serializer.save()
        return Response(sub_activity_we_serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO: Refactor this function to handle validations properly. Also should be generic.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)
        sub_activity_we_object = self.get_object()  # type:SubActivityWorkEntry
        sub_activity_we_object.sub_activity_id = request.data['sub_activity_id']
        sub_activity_we_serializer = self.get_serializer(sub_activity_we_object, data=request.data, partial=partial)
        sub_activity_we_serializer.is_valid(raise_exception=True)
        sub_activity_we_serializer.save()
        return Response(sub_activity_we_serializer.data)
