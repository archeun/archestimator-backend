from django.contrib.auth.models import User

from estimator.models import Estimate


def get_records(request):
    """
    Returns the Estimate objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Estimate.objects.all()
    return Estimate.objects.filter(owner__user__username=request.user)
