from collections import defaultdict
import csv
import io
import os
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

import joblib

from .forms import (
    ClassroomForm,
    FacultyForm,
    GroupForm,
    SubjectForm,
    TeacherForm,
    TimeSlotForm,
)
from .models import (
    Classroom,
    Faculty,
    Group,
    Subject,
    Teacher,
    TIME_SLOTS,
    DAYS_OF_WEEK,
    TimeSlot,
)


# Evolutionary algorithm constants
GENE_POOL_SIZE = 30
ELITE_COUNT = 2
SELECTION_POOL = 8
MUTATION_PROB = 0.05
TRACK_VARS = {
    'gen_count': 0,
    'stop_evolution': False,
}


# ===== Utility functions =====

def run_ai_check(student_count, room_size, has_projector):
    """Evaluate a room assignment via a pre-trained AI model."""
    model_path = os.path.join(os.path.dirname(__file__), 'scheduler_model.pkl')

    try:
        model = joblib.load(model_path)
        output = model.predict([[student_count, room_size, has_projector]])
        return 'AI Approved' if output[0] == 1 else 'AI Warning: Inefficient'
    except Exception:
        return 'AI Offline'


def bulk_upload_csv(request):
    """Handle CSV bulk uploads for the Classroom model."""
    if request.method == 'GET':
        return render(request, 'bulk_upload.html')

    try:
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_upload')

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string, None)  # skip header row

        for row in csv.reader(io_string, delimiter=',', quotechar='|'):
            Classroom.objects.update_or_create(
                room_code=row[0],
                defaults={'capacity': row[1]},
            )

        messages.success(request, 'File uploaded and processed successfully!')
        return redirect('bulk_upload')

    except Exception as exc:
        messages.error(request, f'Error: {exc}')
        return redirect('bulk_upload')


# ===== Data model facades for EA =====


class GenePool:
    def __init__(self, size):
        self._size = size
        self._dataset = dataset
        self._timetables = [Timetable().build() for _ in range(size)]

    def get_timetables(self):
        return self._timetables


class Dataset:
    def __init__(self):
        self._classrooms = Classroom.objects.all()
        self._time_slots = TimeSlot.objects.all()
        self._teachers = Teacher.objects.all()
        self._subjects = Subject.objects.all()
        self._faculties = Faculty.objects.all()
        self._groups = Group.objects.all()

    def get_classrooms(self):
        return self._classrooms

    def get_teachers(self):
        return self._teachers

    def get_subjects(self):
        return self._subjects

    def get_faculties(self):
        return self._faculties

    def get_time_slots(self):
        return self._time_slots

    def get_groups(self):
        return self._groups


class Session:
    def __init__(self, faculty, group, subject):
        self.faculty = faculty
        self.subject = subject
        self.teacher = None
        self.time_slot = None
        self.classroom = None
        self.group = group

    def get_group_id(self):
        return self.group.group_code

    def get_faculty(self):
        return self.faculty

    def get_subject(self):
        return self.subject

    def get_teacher(self):
        return self.teacher

    def get_time_slot(self):
        return self.time_slot

    def get_classroom(self):
        return self.classroom

    def assign_teacher(self, teacher):
        self.teacher = teacher

    def assign_time_slot(self, time_slot):
        self.time_slot = time_slot

    def assign_classroom(self, classroom):
        self.classroom = classroom


class Timetable:
    def __init__(self):
        self._dataset = dataset
        self._sessions = []
        self._conflict_count = 0
        self._score = -1
        self._score_updated = True

    def get_sessions(self):
        self._score_updated = True
        return self._sessions

    def get_conflict_count(self):
        return self._conflict_count

    def get_score(self):
        if self._score_updated:
            self._score = self.compute_score()
            self._score_updated = False
        return self._score

    def add_subject(self, data_obj, subject, subjects, faculty, group):
        new_session = Session(faculty, group, subject)

        new_session.assign_time_slot(random.choice(data_obj.get_time_slots()))
        new_session.assign_classroom(random.choice(data_obj.get_classrooms()))

        subj_teachers = list(subject.assigned_teachers.all())
        if subj_teachers:
            new_session.assign_teacher(random.choice(subj_teachers))

        self._sessions.append(new_session)

    def build(self):
        all_groups = Group.objects.select_related('faculty').all()

        for group in all_groups:
            fac = group.faculty
            required_sessions = min(group.weekly_sessions, len(dataset.get_time_slots()))
            subjects = list(fac.offered_subjects.all())

            if not subjects:
                continue

            sessions_per_subject = required_sessions // len(subjects)
            extra_sessions = required_sessions % len(subjects)

            for subject in subjects:
                for _ in range(sessions_per_subject):
                    self.add_subject(dataset, subject, subjects, fac, group)

            selected_subjects = random.sample(subjects, extra_sessions)
            for subject in selected_subjects:
                self.add_subject(dataset, subject, subjects, fac, group)

        return self

    def compute_score(self):
        self._conflict_count = 0
        sessions = self.get_sessions()

        for i, current in enumerate(sessions):
            if current.classroom.capacity < int(current.subject.max_students):
                self._conflict_count += 1

            for other in sessions[i + 1:]:
                same_subject_same_day = (
                    current.subject.subject_title == other.subject.subject_title
                    and current.time_slot.weekday == other.time_slot.weekday
                )
                teacher_conflict = (
                    current.group != other.group
                    and current.time_slot == other.time_slot
                    and current.teacher == other.teacher
                )
                group_time_conflict = (
                    current.group == other.group
                    and current.time_slot == other.time_slot
                )

                if same_subject_same_day or teacher_conflict or group_time_conflict:
                    self._conflict_count += 1

        return 1 / (self._conflict_count + 1)


class EvolutionaryOptimizer:
    def evolve(self, gene_pool):
        return self._apply_mutation(self._perform_crossover(gene_pool))

    def _perform_crossover(self, pool):
        crossover_pool = GenePool(0)
        elites = pool.get_timetables()[:ELITE_COUNT]
        crossover_pool.get_timetables().extend(elites)

        for _ in range(ELITE_COUNT, GENE_POOL_SIZE):
            parent_a = self._select_parent(pool)
            parent_b = self._select_parent(pool)
            crossover_pool.get_timetables().append(
                self._crossover_timetable(parent_a, parent_b)
            )

        return crossover_pool

    def _apply_mutation(self, pool):
        for i in range(ELITE_COUNT, GENE_POOL_SIZE):
            self._mutate_timetable(pool.get_timetables()[i])
        return pool

    def _crossover_timetable(self, timetable_a, timetable_b):
        offspring = Timetable().build()
        offspring_sessions = []

        for sess_a, sess_b in zip(timetable_a.get_sessions(), timetable_b.get_sessions()):
            selected = sess_a if random.random() > 0.5 else sess_b
            offspring_sessions.append(selected)

        offspring.get_sessions().clear()
        offspring.get_sessions().extend(offspring_sessions)
        return offspring

    def _mutate_timetable(self, timetable):
        fresh_timetable = Timetable().build()
        for idx in range(len(timetable.get_sessions())):
            if MUTATION_PROB > random.random():
                timetable.get_sessions()[idx] = fresh_timetable.get_sessions()[idx]
        return timetable

    def _select_parent(self, pool):
        contenders = random.sample(pool.get_timetables(), SELECTION_POOL)
        return max(contenders, key=lambda t: t.get_score())


def prepare_context(timetable):
    """Convert algorithm timetable sessions into template-friendly dicts."""
    return [
        {
            'group': item.group.group_code,
            'faculty': item.faculty.faculty_name,
            'subject': f'{item.subject.subject_title} ({item.subject.subject_code} {item.subject.max_students})',
            'classroom': f'{item.classroom.room_code} ({item.classroom.capacity})',
            'teacher': f'{item.teacher.full_name} ({item.teacher.teacher_id})',
            'time_slot': [item.time_slot.slot_id, item.time_slot.weekday, item.time_slot.duration],
        }
        for item in timetable.get_sessions()
    ]


def api_gen_count(request):
    return JsonResponse({'genNum': TRACK_VARS['gen_count']})


def api_stop_evolution(request):
    TRACK_VARS['stop_evolution'] = True
    return redirect('home')


# ===== Views =====

@login_required
def timetable(request):
    global dataset
    dataset = Dataset()

    gene_pool = GenePool(GENE_POOL_SIZE)
    TRACK_VARS['gen_count'] = 0
    TRACK_VARS['stop_evolution'] = False

    gene_pool.get_timetables().sort(key=lambda t: t.get_score(), reverse=True)
    optimizer = EvolutionaryOptimizer()
    best_timetable = gene_pool.get_timetables()[0]

    history = [
        {
            'gen': TRACK_VARS['gen_count'],
            'fitness': best_timetable.get_score(),
            'conflicts': best_timetable.get_conflict_count(),
        }
    ]

    while best_timetable.get_score() != 1.0 and TRACK_VARS['gen_count'] < 100:
        if TRACK_VARS['stop_evolution']:
            return HttpResponse('')

        gene_pool = optimizer.evolve(gene_pool)
        gene_pool.get_timetables().sort(key=lambda t: t.get_score(), reverse=True)
        best_timetable = gene_pool.get_timetables()[0]

        TRACK_VARS['gen_count'] += 1
        history.append(
            {
                'gen': TRACK_VARS['gen_count'],
                'fitness': best_timetable.get_score(),
                'conflicts': best_timetable.get_conflict_count(),
            }
        )
        print(f'> Generation #{TRACK_VARS["gen_count"]}, Score: {best_timetable.get_score()}')

    return render(
        request, 'timetable.html', {
            'groups': Group.objects.select_related('faculty').all(),
            'schedule': best_timetable.get_sessions(),
            'time_slots': TIME_SLOTS,
            'week_days': DAYS_OF_WEEK,
            'history': history,
            'pop_size': GENE_POOL_SIZE,
            'mutation_rate': MUTATION_PROB,
            'total_gens': TRACK_VARS['gen_count'],
            'context_data': prepare_context(best_timetable),
        }
    )


def home(request):
    return render(request, 'index.html', {})


@login_required
def teacher_add(request):
    form = TeacherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('teacher_add')

    return render(request, 'teacherAdd.html', {'form': form})


@login_required
def teacher_edit(request):
    return render(request, 'teacherEdit.html', {'teachers': Teacher.objects.all()})


@login_required
def teacher_delete(request, pk):
    if request.method == 'POST':
        Teacher.objects.filter(pk=pk).delete()
        return redirect('teacher_edit')


@login_required
def classroom_add(request):
    form = ClassroomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('classroom_add')

    return render(request, 'classroomAdd.html', {'form': form})


@login_required
def classroom_edit(request):
    return render(request, 'classroomEdit.html', {'classrooms': Classroom.objects.all()})


@login_required
def classroom_delete(request, pk):
    if request.method == 'POST':
        Classroom.objects.filter(pk=pk).delete()
        return redirect('classroom_edit')


@login_required
def time_slot_add(request):
    form = TimeSlotForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('time_slot_add')

    return render(request, 'timeSlotAdd.html', {'form': form})


@login_required
def time_slot_edit(request):
    return render(request, 'timeSlotEdit.html', {'time_slots': TimeSlot.objects.all()})


@login_required
def time_slot_delete(request, pk):
    if request.method == 'POST':
        TimeSlot.objects.filter(pk=pk).delete()
        return redirect('time_slot_edit')


@login_required
def subject_add(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('subject_add')

    return render(request, 'subjectAdd.html', {'form': form})


@login_required
def subject_edit(request):
    teacher_map = defaultdict(list)

    for mapping in Subject.assigned_teachers.through.objects.all():
        subject_code = mapping.subject_id
        teacher_name = (
            Teacher.objects.filter(id=mapping.teacher_id)
            .values_list('full_name', flat=True)
            .first()
        )
        if teacher_name:
            teacher_map[subject_code].append(teacher_name)

    return render(
        request,
        'subjectEdit.html',
        {'subjects': Subject.objects.all(), 'teacher': teacher_map},
    )


@login_required
def subject_delete(request, pk):
    if request.method == 'POST':
        Subject.objects.filter(pk=pk).delete()
        return redirect('subject_edit')


@login_required
def faculty_add(request):
    form = FacultyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('faculty_add')

    return render(request, 'facultyAdd.html', {'form': form})


@login_required
def faculty_edit(request):
    subject_map = defaultdict(list)
    for fac_subject in Faculty.offered_subjects.through.objects.all():
        faculty_name = (
            Faculty.objects.filter(id=fac_subject.faculty_id)
            .values_list('faculty_name', flat=True)
            .first()
        )
        subject_title = (
            Subject.objects.filter(subject_code=fac_subject.subject_id)
            .values_list('subject_title', flat=True)
            .first()
        )
        if faculty_name and subject_title:
            subject_map[faculty_name].append(subject_title)

    return render(
        request,
        'facultyEdit.html',
        {'faculties': Faculty.objects.all(), 'subject': subject_map},
    )


@login_required
def faculty_delete(request, pk):
    if request.method == 'POST':
        Faculty.objects.filter(pk=pk).delete()
        return redirect('faculty_edit')


@login_required
def group_add(request):
    form = GroupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('group_add')

    return render(request, 'groupAdd.html', {'form': form})


@login_required
def group_edit(request):
    return render(request, 'groupEdit.html', {'groups': Group.objects.all()})


@login_required
def group_delete(request, pk):
    if request.method == 'POST':
        Group.objects.filter(pk=pk).delete()
        return redirect('group_edit')


# ===== Error handlers =====


def error_404(request, exception):
    return render(request, 'errors/404.html', {})


def error_500(request, *args, **kwargs):
    return render(request, 'errors/500.html', {})
