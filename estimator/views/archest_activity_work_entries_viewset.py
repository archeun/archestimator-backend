from rest_framework.response import Response

from estimator.models import ActivityWorkEntry, Resource
from estimator.serializers import ActivityWorkEntrySerializer
from estimator.services import work_entries
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


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
