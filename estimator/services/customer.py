from estimator.models import Customer


def get_records(request):
    """
    Returns the Customer objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return Customer.objects.filter(project__phase__resources__user__username=request.user).distinct()
