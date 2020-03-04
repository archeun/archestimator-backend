from estimator.models import Customer
from estimator.serializers import CustomerSerializer
from estimator.services import customer
from estimator.views.archest_authenticated_model_viewset import ArchestAuthenticatedModelViewSet


class CustomerViewSet(ArchestAuthenticatedModelViewSet):
    """
    API endpoint that allows Customers to be viewed or edited.
    """

    queryset = Customer.objects.none()

    def get_queryset(self):
        return customer.get_records(self.request)

    serializer_class = CustomerSerializer
