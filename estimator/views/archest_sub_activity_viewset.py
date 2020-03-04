from rest_framework.decorators import action
from rest_framework.response import Response

from estimator.models import SubActivity
from estimator.serializers import SubActivitySerializer, SubActivityWorkEntrySerializer
from estimator.services import subactivity
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


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
