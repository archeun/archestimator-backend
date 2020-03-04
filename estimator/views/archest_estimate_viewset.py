from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response

from estimator.models import Estimate, Phase, EstimateResource, Activity
from estimator.serializers import EstimateSerializer, ActivitySerializer, EstimateResourceSerializer
from estimator.services import estimate
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


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
