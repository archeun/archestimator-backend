from django.contrib.auth.models import User
from django.db.models import Q

from estimator.models import Activity


def get_records(request):
    """
    Returns the Activity objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Activity.objects.all()
    return Activity.objects.filter(
        Q(estimate__owner__user__username=user)
        | Q(owner__user__username=request.user)
        | Q(owner__user__username__isnull=True)
        | Q(estimate__resources__user__username=user)
    ).distinct()
