from estimator.models import Feature
from estimator.serializers import FeatureSerializer
from estimator.services import feature
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


class FeatureViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Features to be viewed or edited.
    """

    queryset = Feature.objects.none()

    def get_queryset(self):
        return feature.get_records(self.request)

    serializer_class = FeatureSerializer
