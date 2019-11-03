from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Project(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Resource(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=200)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    def full_name(self):
        return self.__str__()


class Phase(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    resources = models.ManyToManyField(Resource, related_name='phase_resources')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    managers = models.ManyToManyField(Resource, related_name='phase_managers')

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=1000)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    def __str__(self):
        return '[' + self.phase.name + '] ' + self.name


class Estimate(models.Model):
    name = models.CharField(max_length=1000)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE)
    resources = models.ManyToManyField(Resource, through='EstimateResource', related_name='estimate_resources')

    def __str__(self):
        return self.name + '[' + self.phase.name + ' : ' + self.owner.user.first_name + ' ' + self.owner.user.last_name + ']'


ESTIMATE_ACCESS_LEVELS = (
    ('1', 'View'),
    ('2', 'Edit')
)


class EstimateResource(models.Model):
    ESTIMATE_ACCESS_LEVELS = ESTIMATE_ACCESS_LEVELS
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=1, choices=ESTIMATE_ACCESS_LEVELS)

    def estimate_id(self):
        return self.estimate.id

    def access_level_name(self):
        return self.get_access_level_display()

    def __str__(self):
        return self.estimate.name + ": " + self.resource.full_name() + ' [' + self.get_access_level_display() + ']'


STATUSES = (
    ('1', 'Backlog'),
    ('2', 'In Progress'),
    ('3', 'Completed'),
    ('4', 'On Hold'),
)


class Activity(models.Model):
    STATUS_CHOICES = STATUSES
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    name = models.CharField(max_length=2000, default='')
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    estimated_time = models.FloatField(default=0)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name

        return 'null'

    def status_name(self):
        return self.get_status_display()


class SubActivity(models.Model):
    STATUS_CHOICES = STATUSES
    name = models.CharField(max_length=2000, default='')
    parent = models.ForeignKey(Activity, on_delete=models.CASCADE)
    estimated_time = models.FloatField(default=0)
    note = models.TextField(max_length=10000, null=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def parent_activity_name(self):
        return self.parent.name

    def parent_activity_id(self):
        return self.parent.id

    def estimate_name(self):
        return self.parent.estimate.name

    def estimate_id(self):
        return self.parent.estimate.id

    def feature_name(self):
        return self.parent.feature.name

    def status_name(self):
        return self.get_status_display()


class ActivityWorkEntry(models.Model):
    ENTRY_TYPE = 'ACTIVITY_WORK_ENTRY_TYPE'
    date = models.DateField()
    worked_hours = models.FloatField(default=0)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    note = models.TextField(max_length=10000, default='', null=True)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.activity.estimate.owner.full_name() + ' worked on Activity ' + self.activity.name + ' on ' \
               + self.date.strftime('%Y-%m-%d') + ' for ' + self.worked_hours.__str__() + ' Hrs.'


class SubActivityWorkEntry(models.Model):
    ENTRY_TYPE = 'SUB_ACTIVITY_WORK_ENTRY_TYPE'
    date = models.DateField()
    worked_hours = models.FloatField(default=0)
    sub_activity = models.ForeignKey(SubActivity, on_delete=models.CASCADE)
    note = models.TextField(max_length=10000, default='', null=True)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.sub_activity.parent.estimate.owner.full_name() + ' worked on Sub Activity ' \
               + self.sub_activity.name + ' on ' + self.date.strftime(
            '%Y-%m-%d') + ' for ' + self.worked_hours.__str__() \
               + ' Hrs.'
