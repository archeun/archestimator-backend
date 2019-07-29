from estimator.models import Estimate


def get_records(request):
    """
    Returns the Estimate objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return Estimate.objects.filter(owner__user__username=request.user)
