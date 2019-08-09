from estimator.models import SubActivity


def get_records(request):
    """
    Returns the Activity objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return SubActivity.objects.filter(parent__estimate__owner__user__username=request.user)
