from django.contrib.auth.models import User

from estimator.models import SubActivity


def get_records(request):
    """
    Returns the Activity objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return SubActivity.objects.all()
    return SubActivity.objects.filter(parent__estimate__owner__user__username=request.user)
