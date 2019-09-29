from django.contrib.auth.models import User

from estimator.models import Estimate
from estimator.serializers import FeatureSerializer


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
    return Estimate.objects.filter(owner__user__username=request.user)


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
                'estimated_time': activity.estimated_time,
                'entered_time_directly_to_activity': entered_time_directly_to_activity,
                'entered_time_to_sub_activities': entered_time_to_sub_activities,
                'status': activity.status,
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
                    'estimated_time': sub_activity.estimated_time,
                    'entered_time': 0,
                    'status': sub_activity.status,
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
                sub_activity_details['remaining_time'] = sub_activity_details['estimated_time'] - sub_activity_work_entry_total_time
                sub_activity_details['completion_percentage'] = get_completion_percentage_for_sub_activity(sub_activity_details)
                activity_details['sub_activities'].append(sub_activity_details)

            activity_details['entered_time_to_sub_activities'] = entered_time_to_sub_activities
            activity_details['total_entered_time'] = activity_details['entered_time_to_sub_activities'] + activity_details['entered_time_directly_to_activity']
            activity_details['remaining_time'] = activity_details['estimated_time'] - activity_details['total_entered_time']
            activity_details['completion_percentage'] = get_completion_percentage_for_activity(activity_details)
            feature_data['activities'].append(activity_details)
        progress['features'].append(feature_data)
    return progress


def get_completion_percentage_for_activity(activity_details):
    completion_percentage = 0
    total_entered = activity_details['entered_time_to_sub_activities'] + activity_details[
        'entered_time_directly_to_activity']
    estimated_time = activity_details['estimated_time']

    if estimated_time > 0:
        completion_percentage = min((total_entered / estimated_time) * 100, 100)

    return round(completion_percentage, 2)


def get_completion_percentage_for_sub_activity(sub_activity_details):
    completion_percentage = 0
    total_entered = sub_activity_details['entered_time']
    estimated_time = sub_activity_details['estimated_time']

    if estimated_time > 0:
        completion_percentage = min((total_entered / estimated_time) * 100, 100)

    return round(completion_percentage, 2)
