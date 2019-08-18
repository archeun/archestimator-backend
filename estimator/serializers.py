from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class ResourceSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Resource
        fields = ('id', 'user', 'full_name')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name',)


class ProjectSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Project
        fields = ('id', 'code', 'name', 'customer')


class PhaseSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    manager = ResourceSerializer()

    class Meta:
        model = Phase
        fields = ('id', 'name', 'project', 'start_date', 'end_date', 'manager')


class FeatureSerializer(serializers.ModelSerializer):
    phase = PhaseSerializer()

    class Meta:
        model = Feature
        fields = ('id', 'name', 'phase',)


class EstimateSerializer(serializers.ModelSerializer):
    phase = PhaseSerializer()
    owner = ResourceSerializer()
    features = FeatureSerializer(source='phase.feature_set', many=True)

    class Meta:
        model = Estimate
        fields = ('id', 'name', 'phase', 'owner', 'features',)


class SubActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubActivity
        fields = ('id', 'name', 'estimated_time', 'note', 'status', 'parent_id', 'STATUS_CHOICES')


class ActivitySerializer(serializers.ModelSerializer):
    feature = FeatureSerializer()
    estimate = EstimateSerializer()
    sub_activities = SubActivitySerializer(source='subactivity_set', many=True)

    class Meta:
        model = Activity
        fields = ('id', 'name', 'feature', 'estimate', 'estimated_time', 'status', 'sub_activities', 'STATUS_CHOICES')


class ActivityWorkEntrySerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()

    class Meta:
        model = ActivityWorkEntry
        fields = ('id', 'date', 'worked_hours', 'activity', 'note',)


class SubActivityWorkEntrySerializer(serializers.ModelSerializer):
    sub_activity = SubActivitySerializer()

    class Meta:
        model = SubActivityWorkEntry
        fields = ('id', 'date', 'worked_hours', 'sub_activity', 'note',)
