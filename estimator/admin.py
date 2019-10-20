from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Project)
admin.site.register(Resource)
admin.site.register(Phase)
admin.site.register(Feature)
admin.site.register(Estimate)
admin.site.register(Activity)
admin.site.register(SubActivity)
admin.site.register(ActivityWorkEntry)
admin.site.register(SubActivityWorkEntry)
admin.site.register(EstimateResources)
