from django.contrib.auth.models import User
from django.db.models import Q

from estimator.models import Project


def get_records(request):
    """
    Returns the Project objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Project.objects.distinct()
    return Project.objects.filter(phase__resources__user__username=request.user).distinct()


def get_phases(request, project_id):
    """
    Returns the Phase objects, created under the given Project and which the user making the given request is added as
    a Resource

    :param project_id: pk of the Project to consider
    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Project.objects.get(pk=project_id).phase_set.all()

    return Project.objects.get(pk=project_id).phase_set.filter(Q(resources__user__username=request.user)).distinct()
