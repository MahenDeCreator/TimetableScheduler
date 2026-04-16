from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('timetableGeneration/', timetable, name='timetable'),

    path('teacherAdd/', teacher_add, name='teacher_add'),
    path('teacherEdit/', teacher_edit, name='teacher_edit'),
    path('teacherDelete/<int:pk>/', teacher_delete, name='delete_teacher'),

    path('classroomAdd/', classroom_add, name='classroom_add'),
    path('classroomEdit/', classroom_edit, name='classroom_edit'),
    path('classroomDelete/<int:pk>/', classroom_delete, name='delete_classroom'),

    path('timeSlotAdd/', time_slot_add, name='time_slot_add'),
    path('timeSlotEdit/', time_slot_edit, name='time_slot_edit'),
    path('timeSlotDelete/<str:pk>/', time_slot_delete, name='delete_time_slot'),

    path('subjectAdd/', subject_add, name='subject_add'),
    path('subjectEdit/', subject_edit, name='subject_edit'),
    path('subjectDelete/<str:pk>/', subject_delete, name='delete_subject'),

    path('facultyAdd/', faculty_add, name='faculty_add'),
    path('facultyEdit/', faculty_edit, name='faculty_edit'),
    path('facultyDelete/<int:pk>/', faculty_delete, name='delete_faculty'),

    path('groupAdd/', group_add, name='group_add'),
    path('groupEdit/', group_edit, name='group_edit'),
    path('groupDelete/<str:pk>/', group_delete, name='delete_group'),

    path('api/genNum/', api_gen_count, name='api_gen_count'),
    path('api/terminateGens/', api_stop_evolution, name='api_stop_evolution'),
    path('upload-csv/', bulk_upload_csv, name='bulk_upload')
]
