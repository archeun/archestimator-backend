from django.contrib.auth.models import User

from estimator.models import Customer


def get_records(request):
    """
    Returns the Customer objects accessible by the user making the given request

    :param request: request object
    :type request: Request
    :return:
    """
    user = request.user  # type:User
    if user.groups.filter(name='Project Admins').exists():
        return Customer.objects.distinct()
    return Customer.objects.filter(project__phase__resources__user__username=request.user).distinct()
