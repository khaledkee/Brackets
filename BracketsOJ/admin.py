from django.contrib import admin
from .models import submission,problem,contest


# Register your models here.
@admin.register(problem)
class ProblemAdmin(admin.ModelAdmin):
    pass


# Register your models here.
@admin.register(submission)
class SubmissionAdmin(admin.ModelAdmin):
    pass


# Register your models here.
@admin.register(contest)
class ContestAdmin(admin.ModelAdmin):
    pass
