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
    managers = ResourceSerializer(read_only=True, many=True)

    class Meta:
        model = Phase
        fields = ('id', 'name', 'project', 'start_date', 'end_date', 'managers')


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


class EstimateResourceSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer()

    class Meta:
        model = EstimateResource
        fields = ('id', 'estimate_id', 'resource', 'access_level', 'access_level_name',)


class SubActivitySerializer(serializers.ModelSerializer):
    owner = ResourceSerializer()
    is_editable = serializers.SerializerMethodField('is_editable_sub_activity', read_only=True)

    def is_editable_sub_activity(self, obj):
        request = self.context['request']
        sub_activity_owner_username = obj.owner.user.username if obj.owner else None
        if request:
            return request.user.username == sub_activity_owner_username\
                   or sub_activity_owner_username is None\
                   or obj.parent.estimate.owner.user.username == request.user.username

    class Meta:
        model = SubActivity
        fields = (
            'id', 'name', 'estimated_time', 'note', 'status', 'parent_id', 'STATUS_CHOICES', 'estimate_name',
            'estimate_id', 'feature_name', 'parent_activity_name', 'parent_activity_id', 'owner', 'is_editable')


class ActivitySerializer(serializers.ModelSerializer):
    feature = FeatureSerializer()
    estimate = EstimateSerializer()
    sub_activities = SubActivitySerializer(source='subactivity_set', many=True)
    owner = ResourceSerializer()
    is_editable = serializers.SerializerMethodField('is_editable_activity', read_only=True)

    def is_editable_activity(self, obj):
        request = self.context['request']
        activity_owner_username = obj.owner.user.username if obj.owner else None
        if request:
            return request.user.username == activity_owner_username or activity_owner_username is None or obj.estimate.owner.user.username == request.user.username

    class Meta:
        model = Activity
        fields = (
            'id', 'name', 'feature', 'estimate', 'estimated_time', 'status', 'sub_activities', 'STATUS_CHOICES',
            'owner', 'is_editable')


class ActivityWorkEntrySerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()

    class Meta:
        model = ActivityWorkEntry
        fields = ('id', 'date', 'worked_hours', 'activity', 'note', 'ENTRY_TYPE')


class SubActivityWorkEntrySerializer(serializers.ModelSerializer):
    sub_activity = SubActivitySerializer()

    class Meta:
        model = SubActivityWorkEntry
        fields = ('id', 'date', 'worked_hours', 'sub_activity', 'note', 'ENTRY_TYPE')
