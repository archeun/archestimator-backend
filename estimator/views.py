from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from estimator.serializers import *
from estimator.services import phase, project, customer
from .models import *


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Customers to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    queryset = Customer.objects.none()

    def get_queryset(self):
        return customer.get_records(self.request)

    serializer_class = CustomerSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Projects to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    queryset = Project.objects.none()

    def get_queryset(self):
        return project.get_records(self.request)

    serializer_class = ProjectSerializer


class PhaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Phases to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    queryset = Phase.objects.none()

    def get_queryset(self):
        return phase.get_records(self.request)

    serializer_class = PhaseSerializer
