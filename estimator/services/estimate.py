from django.contrib.auth.models import User
from django.db.models import Q

from estimator.models import Estimate, EstimateResource


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

    return Estimate.objects.filter(Q(owner__user__username=user) | Q(resources__user__username=request.user)).distinct()


def get_progress(estimate_id):
    estimate = Estimate.objects.get(pk=estimate_id)
    progress = {'estimate': {'name': estimate.name}, 'features': []}
    features = estimate.phase.feature_set.all()
    for feature in features:
        feature_data = {'id': feature.id, 'name': feature.name, 'activities': []}
        activities = feature.activity_set.filter(estimate_id=estimate_id).all()

        for activity in activities:

            entered_time_directly_to_activity = 0
            entered_time_to_sub_activities = 0

            activity_details = {
                'id': activity.id,
                'name': activity.name,
                'owner': activity.owner.full_name() if activity.owner else '',
                'estimated_time': activity.estimated_time,
                'entered_time_directly_to_activity': entered_time_directly_to_activity,
                'entered_time_to_sub_activities': entered_time_to_sub_activities,
                'status': activity.status,
                'status_name': activity.status_name(),
                'work_entries': [],
                'sub_activities': []
            }

            activity_work_entries = activity.activityworkentry_set.all()

            for activity_work_entry in activity_work_entries:
                entered_time_directly_to_activity += activity_work_entry.worked_hours
                activity_details['work_entries'].append(
                    {
                        'id': activity_work_entry.id,
                        'date': activity_work_entry.date,
                        'worked_hours': activity_work_entry.worked_hours,
                        'note': activity_work_entry.note,
                    }
                )
            activity_details['entered_time_directly_to_activity'] = entered_time_directly_to_activity

            sub_activities = activity.subactivity_set.all()
            for sub_activity in sub_activities:
                sub_activity_details = {
                    'id': sub_activity.id,
                    'name': sub_activity.name,
                    'owner': sub_activity.owner.full_name() if sub_activity.owner else '',
                    'estimated_time': sub_activity.estimated_time,
                    'entered_time': 0,
                    'status': sub_activity.status,
                    'status_name': sub_activity.status_name(),
                    'work_entries': []
                }
                sub_activity_work_entries = sub_activity.subactivityworkentry_set.all()
                sub_activity_work_entry_total_time = 0
                for sub_activity_work_entry in sub_activity_work_entries:
                    sub_activity_work_entry_total_time += sub_activity_work_entry.worked_hours
                    sub_activity_details['work_entries'].append(
                        {
                            'id': sub_activity_work_entry.id,
                            'date': sub_activity_work_entry.date,
                            'worked_hours': sub_activity_work_entry.worked_hours,
                            'note': sub_activity_work_entry.note,
                        }
                    )

                entered_time_to_sub_activities += sub_activity_work_entry_total_time
                sub_activity_details['entered_time'] = sub_activity_work_entry_total_time
                sub_activity_details['remaining_time'] = sub_activity_details[
                                                             'estimated_time'] - sub_activity_work_entry_total_time
                sub_activity_details['completion_percentage'] = get_completion_percentage_for_sub_activity(
                    sub_activity_details)
                activity_details['sub_activities'].append(sub_activity_details)

            activity_details['entered_time_to_sub_activities'] = entered_time_to_sub_activities
            activity_details['total_entered_time'] = activity_details['entered_time_to_sub_activities'] + \
                                                     activity_details['entered_time_directly_to_activity']
            activity_details['remaining_time'] = activity_details['estimated_time'] - activity_details[
                'total_entered_time']
            activity_details['completion_percentage'] = get_completion_percentage_for_activity(activity_details)
            feature_data['activities'].append(activity_details)
        progress['features'].append(feature_data)
    return progress


def get_completion_percentage_for_activity(activity_details):
    total_entered = activity_details['entered_time_to_sub_activities'] + activity_details[
        'entered_time_directly_to_activity']
    estimated_time = activity_details['estimated_time']

    if estimated_time > 0:
        completion_percentage = min((total_entered / estimated_time) * 100, 100)
    else:
        completion_percentage = 100

    return round(completion_percentage, 2)


def get_completion_percentage_for_sub_activity(sub_activity_details):
    total_entered = sub_activity_details['entered_time']
    estimated_time = sub_activity_details['estimated_time']

    if estimated_time > 0:
        completion_percentage = min((total_entered / estimated_time) * 100, 100)
    else:
        completion_percentage = 100

    return round(completion_percentage, 2)


def update_shared_resources(estimate, shared_resources_options):
    """
    Updates the EstimateResource which the given estimate is shared with
    :param estimate: Estimate
    :param shared_resources_options: QueryDict
    :return:
    """
    existing_resources = estimate.estimateresource_set.all()
    existing_resource_ids = []
    updated_resource_ids = []
    for existing_resource in existing_resources:
        existing_resource_ids.append(int(existing_resource.resource.id))

    for resource_id in shared_resources_options:
        updated_resource_ids.append(int(resource_id))

    deleted_resource_ids = set(existing_resource_ids) - set(updated_resource_ids)
    newly_added_resource_ids = set(updated_resource_ids) - set(existing_resource_ids)

    for deleted_resource_id in deleted_resource_ids:
        existing_resources.filter(resource_id=deleted_resource_id).delete()

    for resource_id in shared_resources_options:
        access_level = shared_resources_options[resource_id]
        if int(resource_id) in newly_added_resource_ids:
            new_estimate_resource = EstimateResource.objects.create(
                estimate_id=estimate.id,
                resource_id=resource_id,
                access_level=access_level
            )  # type:EstimateResource

            new_estimate_resource.save()
        else:
            existing_resource = existing_resources.get(resource_id=resource_id)
            existing_resource.access_level = access_level
            existing_resource.save()

    return True


def get_shared_resources(estimate_obj, logged_in_username):
    """

    :param mode:
    :param logged_in_username:
    :param estimate_obj:
    :type estimate_obj: Estimate
    :return:
    """

    is_project_admin = User.objects.get(username=logged_in_username).groups.filter(name='Project Admins').exists()
    if estimate_obj.owner.user.username == logged_in_username or is_project_admin:
        return estimate_obj.estimateresource_set
    else:
        return estimate_obj.estimateresource_set.filter(resource__user__username=logged_in_username)
