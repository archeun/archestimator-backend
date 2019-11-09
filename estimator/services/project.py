from django.contrib.auth.models import User

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
