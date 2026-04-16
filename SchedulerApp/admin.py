from django.contrib import admin
from .models import Classroom, Faculty, Group, Subject, Teacher, TimeSlot

admin.site.register(Classroom)
admin.site.register(Teacher)
admin.site.register(TimeSlot)
admin.site.register(Subject)
admin.site.register(Faculty)
admin.site.register(Group)
