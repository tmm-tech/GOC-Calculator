from decimal import Decimal
from multiprocessing import Value
from unittest import case
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Sum, FloatField, CharField, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Semester, Student, Record, SecretKey, RSAKey, Staff,Users, CalculateGp, Sysadmin,Student,Course
from .forms import CalculateGpForm


grade_points = {
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    'D': 1.0,
    'D-': 0.7,
    'F': 0.0,
    'NG': 0.0,
    'S': 0.0,
    'U': 0.0,
    'I': 0.0,
    'W': 0.0,
    'NT': 0.0,
}

def index(request):
    return render(request, 'goc_app/index.html')


from django.db import connection

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

def login_sysadmin(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('sysadmin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'goc_app/login_admin.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'goc_app/login_user.html')


@login_required
def view_records_user(request,username):
    user = get_object_or_404(Users, username=username)
    record = Record.objects.all() # get all Users objects as a queryset
    return render(request, 'goc_app/view_records_user.html', {'users': user,'record':record})



def register_sysadmin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        admin = Sysadmin.objects.create(email=email, is_superuser=True, password=password, first_name=firstname, last_name=lastname, username=username)
        admin.set_password(password)
        admin.save()
        user = User.objects.create_user(email=email, password=password, first_name=firstname, last_name=lastname, username=username, is_superuser=True)
        user.save()
        messages.success(request, 'Sysadmin registered successfully')
        return redirect('login_sysadmin')
    return render(request, 'goc_app/register_admin.html')


def logout_user(request):
    logout(request)
    return redirect('login_user')


def logout_staff(request):
    logout(request)
    return redirect('login_staff')


@login_required
def update_record_staff(request, id):
    student = get_object_or_404(Student, id=id)
    print(f"update records: {id}")
    course = Course.objects.all()
    record =Record.objects.all()
    if request.method == 'POST':
        course_code = request.POST.get("course_name")
        semester = request.POST.get("semester")
        year = request.POST.get("year")
        lec_credits = float(request.POST.get("lec_credits"))
        lab_credits = float(request.POST.get("lab_credits"))
        tut_credits = float(request.POST.get("tut_credits"))
        total_credits = lec_credits + lab_credits + tut_credits
        description = request.POST.get("description")
        grade, grade_desc = None, None
        if total_credits < 0 or total_credits > 4:
            messages.error(request,"Total credits must be between 0 and 4.")
            return redirect("update_record_staff", id=id)
        elif description == "ON PROBATION":
            grade = "S"
            grade_desc = "ON PROBATION"
        elif description == "UNSATISFACTORY":
            grade = "U"
            grade_desc = "UNSATISFACTORY"
        elif description == "INCOMPLETE":
            grade = "I"
            grade_desc = "INCOMPLETE"
        elif description == "COURSE WITHDRAWAL":
            grade = "W"
            grade_desc = "COURSE WITHDRAWAL"
        elif description == "NIL GRADE (FAIL)":
            grade = "NG"
            grade_desc = "NIL GRADE (FAIL)"
        else:
            if total_credits >= 3.7:
                grade = "A"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 3.3:
                grade = "A-"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 3:
                grade = "B+"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 2.7:
                grade = "B"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 2.3:
                grade = "B-"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 2:
                grade = "C+"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 1.7:
                grade = "C"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 1.3:
                grade = "C-"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 1:
                grade = "D+"
                grade_desc = "SATISFACTORY"
            elif total_credits >= 0.7:
                grade = "D"
                grade_desc = "CONDITIONAL PASS"
            else:
                grade = "F"
                grade_desc = "FAIL"
        
        details = Record.objects.create(
            code=course_code,
            year=year,
            semester=semester,
            grade=grade,
            total=total_credits,
            description=grade_desc,
            lec_credits=lec_credits,
            lab_credits=lab_credits,
            tut_credits=tut_credits,
            student_id=id
        )
        details.save()
        messages.success(request, "Record updated successfully.")
        return redirect("update_record_staff", id=id)
    context = {
        "student": student,
        "course": course,
        "record": record,
    }
    return render(request, "goc_app/update_record.html", context)





def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        users = Users.objects.create(email=email, password=password, firstname=firstname, lastname=lastname, username=username)
        users.set_password(password)
        users.save()
        user = User.objects.create_user(email=email, password=password, first_name=firstname, last_name=lastname, username=username)
        user.save()
        messages.success(request, 'Sysadmin registered successfully')
        return redirect('login_user')
    return render(request, 'goc_app/register_user.html')


@login_required(login_url='login_user')
def dashboard(request):
    return render(request, 'goc_app/dashboard.html')

@login_required(login_url='login_staff')
def dashboard_staff(request):
    return render(request, 'goc_app/dashboard_staff.html')

@login_required(login_url='login_sysadmin')
def dashboard_admin(request):
    return render(request, 'goc_app/dashboard_admin.html')

@login_required(login_url='login_sysadmin')
def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        student = Users.objects.create(email=email, password=password, firstname=firstname, lastname=lastname, username=username)
        students = Student.objects.create(email=email, password=password, firstname=firstname, lastname=lastname, username=username)
        students.save()
        student.set_password(password)
        student.save()
        user = User.objects.create_user(email=email, password=password, first_name=firstname, last_name=lastname, username=username)
        user.save()
        messages.success(request, 'User registered successfully')
        return redirect('view_users')
    return render(request, 'goc_app/add_user.html')

@login_required(login_url='login_sysadmin')
def logout_sysadmin(request):
    logout(request)
    return redirect('login_sysadmin')

@login_required(login_url='login_sysadmin')
def view_users(request):
    users = Users.objects.all()
    return render(request, 'goc_app/view_records_admin.html', {'users': users})


def register_staff(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        staff = Staff(email=email, password=password, firstname=firstname, lastname=lastname, username=username)
        staff.set_password(password)
        staff.save()
        user = User.objects.create_user(email=email, password=password, first_name=firstname, last_name=lastname, username=username, is_staff=True)
        user.save()
        messages.success(request, 'Staff registered successfully')
        return redirect('login_staff')
    return render(request, 'goc_app/register_staff.html')

def login_staff(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'goc_app/login_staff.html')

@login_required(login_url='login_staff')
def view_records_staff(request):
        student = Student.objects.all()
        return render(request, 'goc_app/view_records_staff.html', {'student': student})

@login_required(login_url='login_staff')
def add_staff_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        student = Student.objects.create(email=email, username=username, password=password, firstname=first_name, lastname=last_name)
        student.set_password(password)
        student.save()
        students = Users.objects.create(email=email, username=username, password=password, firstname=first_name, lastname=last_name)
        students.set_password(password)
        students.save()
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        user.save()
        messages.success(request, 'Student user registered successfully')
        return redirect('staff_dashboard')
    return render(request, 'goc_app/staff_userregister.html')

@login_required(login_url='login_user')
def calculate_gp(request,username):
    user = get_object_or_404(Users, username=username)
    student=Record.objects.all()
    return render(request, 'goc_app/calculate_gp_user.html', {'student': student, 'user': user})

def add_course(request):
    if request.method == 'POST':
        code = request.POST.get('course_code')
        title = request.POST.get('course_title')
        course = Course.objects.create(course_code=code, course_title=title)
        course.save()
        messages.success(request, 'Course Added successfully')
        return redirect('staff_dashboard')
    return render(request, 'goc_app/add_course.html')

def calculate_grade(request):
    lec_credits = float(request.form.get("lec_credits"))
    lab_credits = float(request.form.get("lab_credits"))
    tut_credits = float(request.form.get("tut_credits"))
    total_credits = lec_credits + lab_credits + tut_credits
    grade, des = None, None
    description = request.form.get("description")
    if total_credits < 0 or total_credits > 4:
        messages.error(request,"Total credits must be between 0 and 4.")
        return redirect("update_record_staff")
    if description == "ON PROBATION":
        grade = "S"
        des = "ON PROBATION"
    elif description == "UNSATISFACTORY":
        grade = "U"
        des = "UNSATISFACTORY"
    elif description == "INCOMPLETE":
        grade = "I"
        des = "INCOMPLETE"
    elif description == "COURSE WITHDRAWAL":
        grade = "W"
        des = "COURSE WITHDRAWAL"
    elif description == "NIL GRADE (FAIL)":
        grade = "NG"
        des = "NIL GRADE (FAIL)"
    else:
        if total_credits == 4:
            grade = "A"
            des = "SATISFACTORY"
        elif total_credits < 4 and total_credits >= 3.7:
            grade = "A-"
            des = "SATISFACTORY"
        elif total_credits < 3.7 and total_credits >= 3.3:
            grade = "B+"
            des = "SATISFACTORY"
        elif total_credits < 3.3 and total_credits >= 3:
            grade = "B"
            des = "SATISFACTORY"
        elif total_credits < 3 and total_credits >= 2.7:
            grade = "B-"
            des = "SATISFACTORY"
        elif total_credits < 2.7 and total_credits >= 2.3:
            grade = "C+"
            des = "SATISFACTORY"
        elif total_credits < 2.3 and total_credits >= 2:
            grade = "C"
            des = "SATISFACTORY"
        elif total_credits < 2 and total_credits >= 1.7:
            grade = "C-"
            des = "SATISFACTORY"
        elif total_credits < 1.7 and total_credits >= 1.3:
            grade = "D+"
            des = "SATISFACTORY"
        elif total_credits < 1.3 and total_credits >= 1:
            grade = "D"
            des = "CONDITIONAL PASS"
        elif total_credits < 1 and total_credits >= 0.7:
            grade = "D-"
            des = "FAIL"
        elif total_credits < 0.7 and total_credits >= 0:
            grade = "F"
            des = "FAIL"
        else:
            messages.error(request,"Invalid credit value entered!")
            return redirect("update_record_staff")
    return render(request,"goc_app/update_record.html", total_credits=total_credits, grade=grade, description=des)


def calculate_gpa(request):
    if request.method == 'GET':
        year = request.GET.get('year')
        semester = request.GET.get('semester')
        
        # Get the student object with the current user's username
         # Get the student object with the current user's username
        student = Student.objects.get(username=request.user.username)     
        # Get the student's ID
        student_id = student.id
        # Filter the records by the student's ID, year, and semester
        courses = Record.objects.filter(student_id=student_id, year=year, semester=semester)
        
        if len(courses) == 0:
            return render(request, 'goc_app/calculate_gp_user.html', {'student': None})
        else:
            return render(request, 'goc_app/calculate_gp_user.html', {'student': courses})
    elif request.method == 'POST':
        student = Student.objects.get(username=request.user.username)
        student_id = student.id
        courses = Record.objects.filter(student_id=student_id)
        total_credits = courses.aggregate(total_credits=Sum('total'))['total_credits']  
        student = Student.objects.get(username=request.user.username)
        student_id = student.id
        courses = Record.objects.filter(student_id=student_id)
        total_credits = courses.aggregate(total_credits=Sum('total'))['total_credits']
        quality_sum = 0
        for course in courses:
            grade_point = grade_points.get(course.grade, 0.0)
            quality_points = float(course.total) * grade_point
            print(quality_points)
            quality_sum += quality_points
        points = float(quality_sum) / float(total_credits)
        print(points)
        gpa = round(points, 2)
        cgpa = round(points, 2)
        print(gpa)
        return render(request, 'goc_app/calculate_gp_user.html', {'student': courses, 'gpa': gpa, 'cgpa': cgpa})
    else:
        return HttpResponse('Invalid request method.')