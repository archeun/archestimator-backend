from estimator.models import Project


def get_records(request):
    """
    Returns the Project objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    return Project.objects.filter(phase__resources__user__username=request.user).distinct()
