from estimator.models import Activity


def get_records(request):
    """
    Returns the Activity objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return Activity.objects.filter(estimate__owner__user__username=request.user)
