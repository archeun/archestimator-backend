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
    resources = models.ManyToManyField(Resource)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    manager = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='phase_manager')

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

    def __str__(self):
        return self.name + '[' + self.phase.name + ' : ' + self.owner.user.first_name + ' ' + self.owner.user.last_name + ']'


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

    def __str__(self):
        if self.name:
            return self.name

        return 'null'


class SubActivity(models.Model):
    STATUS_CHOICES = STATUSES
    name = models.CharField(max_length=2000, default='')
    parent = models.ForeignKey(Activity, on_delete=models.CASCADE)
    estimated_time = models.FloatField(default=0)
    note = models.TextField(max_length=10000, null=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name
