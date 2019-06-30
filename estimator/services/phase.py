from estimator.models import Phase


def get_records(request):
    """
    Returns the Phase objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return Phase.objects.filter(resources__user__username=request.user)
