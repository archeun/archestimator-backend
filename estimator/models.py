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


class Phase(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Customer, on_delete=models.CASCADE)
    resources = models.ManyToManyField(Resource)

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=1000)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    def __str__(self):
        return '[' + self.phase.name + '] ' + self.name


class Estimate(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    owner = models.ForeignKey(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return self.feature.name + ' : ' + self.owner.user.first_name + ' ' + self.owner.user.last_name


class Activity(models.Model):
    name = models.CharField(max_length=2000)
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    estimated_time = models.IntegerField()
    is_completed = models.BooleanField()

    def __str__(self):
        return self.name


class SubActivity(models.Model):
    name = models.CharField(max_length=2000)
    parent = models.ForeignKey(Activity, on_delete=models.CASCADE)
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE)
    estimated_time = models.IntegerField()
    is_completed = models.BooleanField()

    def __str__(self):
        return self.name
