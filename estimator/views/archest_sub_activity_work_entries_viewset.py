from rest_framework.response import Response

from estimator.models import SubActivityWorkEntry, Resource
from estimator.serializers import SubActivityWorkEntrySerializer
from estimator.services import work_entries
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


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
