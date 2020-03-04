from django.contrib.auth.models import User

from estimator.models import Feature


def get_records(request):
    """
    Returns the Feature objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Feature.objects.distinct()
    return Feature.objects.filter(phase__resources__user__username=request.user).distinct()
