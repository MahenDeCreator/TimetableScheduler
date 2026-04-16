"""Domain models and shared scheduling constants."""

from django.db import models


TIME_SLOTS = (
    ('8:45 - 9:45', '8:45 - 9:45'),
    ('10:00 - 11:00', '10:00 - 11:00'),
    ('11:00 - 12:00', '11:00 - 12:00'),
    ('1:00 - 2:00', '1:00 - 2:00'),
    ('2:15 - 3:15', '2:15 - 3:15'),
)

DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
)


class Classroom(models.Model):
    room_code = models.CharField(max_length=6, unique=True)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.room_code


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=6, unique=True)
    full_name = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.teacher_id} {self.full_name}'


class TimeSlot(models.Model):
    slot_id = models.CharField(max_length=4, primary_key=True)
    duration = models.CharField(
        max_length=50,
        choices=TIME_SLOTS,
        default='11:30 - 12:30',
    )
    weekday = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.slot_id} {self.weekday} {self.duration}'


class Subject(models.Model):
    subject_code = models.CharField(max_length=5, primary_key=True)
    subject_title = models.CharField(max_length=40)
    max_students = models.CharField(max_length=65)
    assigned_teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return f'{self.subject_code} {self.subject_title}'


class Faculty(models.Model):
    faculty_name = models.CharField(max_length=50)
    offered_subjects = models.ManyToManyField(Subject)

    @property
    def get_subjects(self):
        return self.offered_subjects

    def __str__(self):
        return self.faculty_name


class Group(models.Model):
    group_code = models.CharField(max_length=25, primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    weekly_sessions = models.IntegerField(default=0)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def set_classroom(self, classroom):
        self.classroom = classroom
        self.save(update_fields=['classroom'])

    def set_time_slot(self, time_slot):
        self.time_slot = time_slot
        self.save(update_fields=['time_slot'])

    def set_teacher(self, teacher):
        self.teacher = teacher
        self.save(update_fields=['teacher'])
