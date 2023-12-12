from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from .decorators import lecturer_required, student_required, admin_required
from course.models import Course
from result.models import TakenCourse
from app.models import Session, Semester
from .forms import StaffAddForm, StudentAddForm, ProfileUpdateForm, ParentAddForm
from .models import User, Student, Parent


def validate_username(request):
    username = request.GET.get("username", None)
    data = {
        "is_taken": User.objects.filter(username__iexact = username).exists()
    }
    return JsonResponse (data)


def register(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hisob muvaffaqiyatli yaratildi.')
        else:
            messages.error(request, f'Nimadir noto‘g‘ri, Iltimos barcha maydonlarni to‘g‘ri to‘ldiring.')
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {'form': form})


@login_required
def profile(request):
    """ So'rovni rad etgan har qanday foydalanuvchining profilini ko'rsatish """
    try:
        current_session = get_object_or_404(Session, is_current_session=True)
        current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
        
    except Semester.MultipleObjectsReturned and Semester.DoesNotExist and Session.DoesNotExist:
        raise Http404

    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(
            semester=current_semester)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        })
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=level)
        except:
            parent = "no parent set"
        courses = TakenCourse.objects.filter(student__student__id=request.user.id, course__level=level.level)
        context = {
            'title': request.user.get_full_name,
            'parent': parent,
            'courses': courses,
            'level': level,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile.html', context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "staff": staff,
            'current_session': current_session,
            'current_semester': current_semester,
        })


@login_required
@admin_required
def profile_single(request, id):
    """ Tanlangan foydalanuvchining profilini ko'rsatish """
    if request.user.id == id:
        return redirect("/profile/")

    current_session = get_object_or_404(Session, is_current_session=True)
    current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(semester=current_semester)
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "O'qituvchi",
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(student__student__id=id, course__level=student.level)
        context = {
            'title': user.get_full_name,
            'user': user,
            "user_type": "Talaba",
            'courses': courses,
            'student': student,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    else:
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "Boshliq",
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)


@login_required
@admin_required
def admin_panel(request):
    return render(request, 'setting/admin_panel.html', {})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilingiz muvaffaqiyatli yangilandi.')
            return redirect('profile')
        else:
            messages.error(request, 'Quyidagi xatolarni tuzating.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'setting/profile_info_change.html', {
        'title': 'Sozlamalar | Student LMS',
        'form': form,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parolingiz muvaffaqiyatli yangilandi!')
            return redirect('profile')
        else:
            messages.error(request, 'Quyidagi xatolarni tuzating. ')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'setting/password_change.html', {
        'form': form,
    })
# ########################################################
# O'qituvchi uchun hisob
@login_required
@admin_required
def staff_add_view(request):
    if request.method == 'POST':
        form = StaffAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, "O'qituvchi uchun hisob" + first_name + ' ' + last_name + " yaratilgan.")
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()

    context = {
        'title': 'O\'qituvchi qo\'shish| Student LMS',
        'form': form,
    }

    return render(request, 'accounts/add_staff.html', context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, 'O''qituvchi ' + full_name + ' yangilandi.')
            return redirect('lecturer_list')
        else:
            messages.error(request, 'Quyidagi xatoni tuzating.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_lecturer.html', {
        'title': 'O\'qituvchini taxrirlash | Student LMS',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "O'qtivchi | Student LMS"
        return context


# @login_required
# @lecturer_required
# def delete_staff(request, pk):
#     staff = get_object_or_404(User, pk=pk)
#     staff.delete()
#     return redirect('lecturer_list')

@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, 'O\'qituvchi ' + full_name + ' o\'chirildi.')
    return redirect('lecturer_list')
# ########################################################


# ########################################################
# Student views
# ########################################################
@login_required
@admin_required
def student_add_view(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, 'Hisob: ' + first_name + ' ' + last_name + 'yaratilindi.')
            return redirect('student_list')
        else:
            messages.error(request, 'Quyidagi xatolarni tuzating.')
    else:
        form = StudentAddForm()

    return render(request, 'accounts/add_student.html', {
        'title': "Talaba qo'shish | Student LMS",
        'form': form
    })


@login_required
@admin_required
def edit_student(request, pk):
    # instance = User.objects.get(pk=pk)
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ('Talaba ' + full_name + ' yangilani.'))
            return redirect('student_list')
        else:
            messages.error(request, 'Quyidagi xatoni tuzating.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_student.html', {
        'title': 'Hisob taxrirlash | Student LMS',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class StudentListView(ListView):
    template_name = "accounts/student_list.html"
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get('student_id')
        if query is not None:
            queryset = queryset.filter(Q(department=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Talabalar | Student LMS"
        return context


@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # full_name = student.user.get_full_name
    student.delete()
    messages.success(request, 'Talaba o\'chirildi')
    return redirect('student_list')
# ########################################################


class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = 'accounts/parent_form.html'


# def parent_add(request):
#     if request.method == 'POST':
#         form = ParentAddForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('student_list')
#     else:
#         form = ParentAddForm(request.POST)
