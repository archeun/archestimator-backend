from rest_framework.decorators import action
from rest_framework.response import Response

from estimator.models import Activity
from estimator.serializers import ActivitySerializer, ActivityWorkEntrySerializer
from estimator.services import activity
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


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
