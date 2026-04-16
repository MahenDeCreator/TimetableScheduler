from django.test import TestCase

from .forms import (
    ClassroomForm,
    FacultyForm,
    GroupForm,
    SubjectForm,
    TeacherForm,
    TimeSlotForm,
)
from .models import Teacher, TimeSlot, Classroom


class SchedulerAppModelFormTests(TestCase):
    def test_classroom_string_representation(self):
        classroom = Classroom(r_number='A101', seating_capacity=30)
        self.assertEqual(str(classroom), 'A101')

    def test_teacher_string_representation(self):
        teacher = Teacher(uid='T001', name='Jane Doe')
        self.assertEqual(str(teacher), 'T001 Jane Doe')

    def test_time_slot_string_representation(self):
        time_slot = TimeSlot(pid='TS1', time='8:45 - 9:45', day='Monday')
        self.assertEqual(str(time_slot), 'TS1 Monday 8:45 - 9:45')

    def test_classroom_form_valid_data(self):
        form = ClassroomForm(data={'r_number': 'B100', 'seating_capacity': 20})
        self.assertTrue(form.is_valid())

    def test_teacher_form_valid_data(self):
        form = TeacherForm(data={'uid': 'T005', 'name': 'Alex Doe'})
        self.assertTrue(form.is_valid())

    def test_time_slot_form_valid_data(self):
        form = TimeSlotForm(data={'pid': 'TS2', 'time': '10:00 - 11:00', 'day': 'Tuesday'})
        self.assertTrue(form.is_valid())
