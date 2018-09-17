from django.contrib import admin
from .models import Company, Report
# from django.contrib.auth.models import User, Group


admin.site.register(Company)
admin.site.register(Report)

# admin.site.unregister(User)
# admin.site.unregister(Group)

