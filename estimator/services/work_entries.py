from django.contrib.auth.models import User

from estimator.models import ActivityWorkEntry, SubActivityWorkEntry


def get_activity_work_entries(request):
    """
    Returns the ActivityWorkEntry objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return: QuerySet
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return ActivityWorkEntry.objects.all()
    return ActivityWorkEntry.objects.filter(activity__estimate__owner__user__username=user)


def get_sub_activity_work_entries(request):
    """
    Returns the SubActivityWorkEntry objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return: QuerySet
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return SubActivityWorkEntry.objects.all()
    return SubActivityWorkEntry.objects.filter(sub_activity__parent__estimate__owner__user__username=user)
