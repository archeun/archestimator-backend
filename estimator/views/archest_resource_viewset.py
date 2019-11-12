from estimator.models import Resource
from estimator.serializers import ResourceSerializer
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


class ResourceViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Resources to be viewed or edited.
    """

    queryset = Resource.objects.all()

    serializer_class = ResourceSerializer
