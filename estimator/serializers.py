from .models import *
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('name',)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('code', 'name', 'customer')


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ('name',)
