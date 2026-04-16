"""Form definitions for the timetable scheduler application."""

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm

from .model_definitions import Subject, Faculty, Teacher, TimeSlot, Classroom, Group


def _build_text_widget(placeholder, element_id):
    return forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': placeholder,
            'id': element_id,
        }
    )


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=_build_text_widget('UserName', 'id_username'))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'type': 'password',
                'placeholder': 'Password',
                'id': 'id_password',
            }
        )
    )


class ClassroomForm(ModelForm):
    class Meta:
        model = Classroom
        fields = ['room_code', 'capacity']
        labels = {'room_code': 'Room Code'}


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'full_name']
        labels = {
            'teacher_id': 'Teacher ID',
            'full_name': 'Full Name',
        }


class TimeSlotForm(ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['slot_id', 'duration', 'weekday']
        widgets = {
            'slot_id': forms.TextInput(),
            'duration': forms.Select(),
            'weekday': forms.Select(),
        }


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_title', 'max_students', 'assigned_teachers']
        labels = {'max_students': 'Maximum Students'}


class FacultyForm(ModelForm):
    class Meta:
        model = Faculty
        fields = ['faculty_name', 'offered_subjects']
        labels = {'faculty_name': 'Faculty Name'}


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['group_code', 'faculty', 'weekly_sessions']
        labels = {'weekly_sessions': 'Sessions per Week'}
