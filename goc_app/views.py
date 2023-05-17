import binascii
import hashlib
import hmac
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from multiprocessing import Value
from unittest import case
from django import forms
from django.http import HttpResponse
from pyDes import des, PAD_PKCS5
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Sum, FloatField, CharField, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import RSAKeyPair, Student, Record, SecretKey, RSAKeyPair, Staff,Users, CalculateGp, Sysadmin,Student,Course,update_des_key
from .forms import CalculateGpForm, DESKeyForm, RSAKeyPairForm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

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
    users = Users.objects.all()
    try:
        secret = SecretKey.objects.get()
    except SecretKey.DoesNotExist:
        secret = None
    if not secret:
        return redirect('update_key')
    des_cipher = des(secret.key, padmode=PAD_PKCS5)

    decrypted_users = []
    for student in users:
        id = student.id
            # Convert hexadecimal encrypted data to bytes
        encrypted_username = binascii.unhexlify(student.username)

        decrypted_username = des_cipher.decrypt(encrypted_username).decode('utf-8')
        
        decrypted_user = {
            'id':id,
            'email': decrypted_username,
        }
        print(decrypted_user)
        
        decrypted_users.append(decrypted_user)
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
    secret=SecretKey.objects.get()
    
    des_cipher = des(secret.key, padmode=PAD_PKCS5)
    encrypted_first_name = binascii.unhexlify(student.firstname)
    encrypted_last_name = binascii.unhexlify(student.lastname)
    decrypted_first_name = des_cipher.decrypt(encrypted_first_name).decode('utf-8')
    decrypted_last_name = des_cipher.decrypt(encrypted_last_name).decode('utf-8')
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
        code=des_cipher.encrypt(course_code.encode('utf-8'))
        year=des_cipher.encrypt(year.encode('utf-8'))
        semester=des_cipher.encrypt(semester.encode('utf-8'))
        grade=des_cipher.encrypt(grade.encode('utf-8'))
        total=des_cipher.encrypt(str(total_credits).encode('utf-8'))
        description=des_cipher.encrypt(grade_desc.encode('utf-8'))
        lec_credits=des_cipher.encrypt(str(lec_credits).encode('utf-8'))
        lab_credits=des_cipher.encrypt(str(lab_credits).encode('utf-8'))
        tut_credits=des_cipher.encrypt(str(tut_credits).encode('utf-8'))
        
        details = Record.objects.create(
            code=binascii.hexlify(code).decode('utf-8'),
            year=binascii.hexlify(year).decode('utf-8'),
            semester=binascii.hexlify(semester).decode('utf-8'),
            grade=binascii.hexlify(grade).decode('utf-8'),
            total=binascii.hexlify(total).decode('utf-8'),
            description=binascii.hexlify(description).decode('utf-8'),
            lec_credits=binascii.hexlify(lec_credits).decode('utf-8'),
            lab_credits=binascii.hexlify(lab_credits).decode('utf-8'),
            tut_credits=binascii.hexlify(tut_credits).decode('utf-8'),
            student_id=id
        )
        details.save()
        messages.success(request, "Record updated successfully.")
        return redirect("update_record_staff", id=id)
    decrypted_records = []
    for recod in record:
        id= recod.id
            # Convert hexadecimal encrypted data to bytes
        code = binascii.unhexlify(recod.code)
        year = binascii.unhexlify(recod.year)
        semester = binascii.unhexlify(recod.semester)
        total = binascii.unhexlify(recod.total)
        grade = binascii.unhexlify(recod.grade)
        description = binascii.unhexlify(recod.description)
        lec = binascii.unhexlify(recod.lec_credits) 
        lab = binascii.unhexlify(recod.lab_credits)
        tut  = binascii.unhexlify(recod.tut_credits)

        # Decrypt the student details
        code = des_cipher.decrypt(code).decode('utf-8')
        year = des_cipher.decrypt(year).decode('utf-8')
        semester = des_cipher.decrypt(semester).decode('utf-8')
        total = des_cipher.decrypt(total).decode('utf-8')
        grade = des_cipher.decrypt(grade).decode('utf-8')
        description = des_cipher.decrypt(description).decode('utf-8')
        lec = des_cipher.decrypt(lec).decode('utf-8')
        lab = des_cipher.decrypt(lab).decode('utf-8')
        tut  = des_cipher.decrypt(tut).decode('utf-8')
        
        decrypted_record = {
            'id':id,
            'code': code,
            'year': year,
            'semester': semester,
            'total': total,
            'grade': grade,
            'description':description,
            'lec_credits':lec,
            'lab_credits':lab,
            'tut_credits':tut
        }
    
        decrypted_records.append(decrypted_record) 
        
    context = {
        "student": student,
        "course": course,
        "record": decrypted_records,
        "name":decrypted_first_name,
        "last":decrypted_last_name
    }
    return render(request, "goc_app/update_record.html", context)

def update_des_key_view(request):
    if request.method == 'POST':
        form = DESKeyForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            # Add your custom conditions here
            if not key.isalpha():
                form.add_error('key', 'Key must contain only alphabetic characters.')
            elif len(key) != 8:
                form.add_error('key', 'Key must be exactly 8 characters long.')
            else:
                encoded_key = key.encode()  # Encode the key to bytes
                secret_key = SecretKey.objects.first()
                if secret_key:
                    secret_key.key = encoded_key
                    secret_key.save()
                else:
                    SecretKey.objects.create(key=encoded_key)
                return redirect('staff_dashboard')
    else:
        form = DESKeyForm()
    
    return render(request, 'goc_app/update_des_key.html', {'form': form})



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
        return redirect('sysadmin_dashboard')
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



def view_records_staff(request):
    students = Student.objects.all()
    try:
        secret = SecretKey.objects.get()
    except SecretKey.DoesNotExist:
        secret = None
    if not secret:
        return redirect('update_key')
    des_cipher = des(secret.key, padmode=PAD_PKCS5)

    decrypted_students = []
    for student in students:
        id= student.id
            # Convert hexadecimal encrypted data to bytes
        encrypted_email = binascii.unhexlify(student.email)
        encrypted_password = binascii.unhexlify(student.password)
        encrypted_first_name = binascii.unhexlify(student.firstname)
        encrypted_last_name = binascii.unhexlify(student.lastname)
        encrypted_username = binascii.unhexlify(student.username)

        # Decrypt the student details
        decrypted_email = des_cipher.decrypt(encrypted_email).decode('utf-8')
        decrypted_password = des_cipher.decrypt(encrypted_password).decode('utf-8')
        decrypted_first_name = des_cipher.decrypt(encrypted_first_name).decode('utf-8')
        decrypted_last_name = des_cipher.decrypt(encrypted_last_name).decode('utf-8')
        decrypted_username = des_cipher.decrypt(encrypted_username).decode('utf-8')
        
        decrypted_student = {
            'id':id,
            'email': decrypted_email,
            'password': decrypted_password,
            'firstname': decrypted_first_name,
            'lastname': decrypted_last_name,
            'username': decrypted_username,
            'date_joined':student.date_joined
        }
        
        decrypted_students.append(decrypted_student)

    return render(request, 'goc_app/view_records_staff.html', {'students': decrypted_students})






@login_required(login_url='login_staff')
def add_staff_user(request):
    try:
        secret = SecretKey.objects.get()
    except SecretKey.DoesNotExist:
        secret = None
    if not secret:
        return redirect('update_key')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        # Encrypt the user details using DES
        # Create the des_cipher object
            # Create the des_cipher object
        des_cipher = des(secret.key, padmode=PAD_PKCS5)

        # Encrypt the student details
        encrypted_email = des_cipher.encrypt(email.encode('utf-8'))
        encrypted_password = des_cipher.encrypt(password.encode('utf-8'))
        encrypted_first_name = des_cipher.encrypt(first_name.encode('utf-8'))
        encrypted_last_name = des_cipher.encrypt(last_name.encode('utf-8'))
        encrypted_username = des_cipher.encrypt(username.encode('utf-8'))

        # Convert encrypted data to hexadecimal
        encrypted_email = binascii.hexlify(encrypted_email).decode('utf-8')
        encrypted_password = binascii.hexlify(encrypted_password).decode('utf-8')
        encrypted_first_name = binascii.hexlify(encrypted_first_name).decode('utf-8')
        encrypted_last_name = binascii.hexlify(encrypted_last_name).decode('utf-8')
        encrypted_username = binascii.hexlify(encrypted_username).decode('utf-8')


         # Create and save the encrypted user details
        student = Student.objects.create(email=encrypted_email, username=encrypted_username, password=encrypted_password, firstname=encrypted_first_name, lastname=encrypted_last_name)
        student.save()
        students = Users.objects.create(email=email, username=username, password=password, firstname=first_name, lastname=last_name)
        students.save()
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        user.save()
        messages.success(request, 'Student user registered successfully')
        return redirect('staff_dashboard')
    return render(request, 'goc_app/staff_userregister.html')

@login_required(login_url='login_user')
def calculate_gp(request,username):
    user = get_object_or_404(Users, username=username)
    record = Record.objects.all() # get all Users objects as a queryset
    try:
        secret = SecretKey.objects.get()
    except SecretKey.DoesNotExist:
        secret = None
    if not secret:
        return redirect('update_key')
    des_cipher = des(secret.key, padmode=PAD_PKCS5)
    decrypted_records = []
    for recod in record:
        id= recod.id
            # Convert hexadecimal encrypted data to bytes
        code = binascii.unhexlify(recod.code)
        year = binascii.unhexlify(recod.year)
        semester = binascii.unhexlify(recod.semester)
        total = binascii.unhexlify(recod.total)
        grade = binascii.unhexlify(recod.grade)
        description = binascii.unhexlify(recod.description)
        lec = binascii.unhexlify(recod.lec_credits) 
        lab = binascii.unhexlify(recod.lab_credits)
        tut  = binascii.unhexlify(recod.tut_credits)

        # Decrypt the student details
        code = des_cipher.decrypt(code).decode('utf-8')
        year = des_cipher.decrypt(year).decode('utf-8')
        semester = des_cipher.decrypt(semester).decode('utf-8')
        total = des_cipher.decrypt(total).decode('utf-8')
        grade = des_cipher.decrypt(grade).decode('utf-8')
        description = des_cipher.decrypt(description).decode('utf-8')
        lec = des_cipher.decrypt(lec).decode('utf-8')
        lab = des_cipher.decrypt(lab).decode('utf-8')
        tut  = des_cipher.decrypt(tut).decode('utf-8')
        
        decrypted_record = {
            'id':id,
            'code': code,
            'year': year,
            'semester': semester,
            'total': total,
            'grade': grade,
            'description':description,
            'lec_credits':lec,
            'lab_credits':lab,
            'tut_credits':tut
        }
    
        decrypted_records.append(decrypted_record) 
        print(decrypted_records)
    return render(request, 'goc_app/calculate_gp_user.html', {'users': user,'record':decrypted_records})


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


def update_rsa_key_pair(request):
    try:
        rsa_key_pair = RSAKeyPair.objects.latest('created_at')
    except RSAKeyPair.DoesNotExist:
        rsa_key_pair = None

    if request.method == 'POST':
        form = RSAKeyPairForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data['public_key']
            private_key = form.cleaned_data['private_key']
            rsa_key_pair = RSAKeyPair.objects.create(public_key=public_key.encode(), private_key=private_key.encode())
            return redirect('staff_dashboard')
    else:
        form = RSAKeyPairForm()

    return render(request, 'goc_app/update_rsa_key_pair.html', {'form': form, 'rsa_key_pair': rsa_key_pair})

def calculate_gpa(request):
    if request.method == 'GET':
        year = request.GET.get('year')
        semester = request.GET.get('semester')
        secret = SecretKey.objects.get()
        des_cipher = des(secret.key, padmode=PAD_PKCS5)
        # Decrypt the username
        encrypted_username = des_cipher.encrypt(request.user.username.encode('utf-8'))
        encrypted_user = binascii.hexlify(encrypted_username).decode('utf-8')
        encrypted_year = des_cipher.encrypt(year.encode('utf-8'))
        year = binascii.hexlify(encrypted_year).decode('utf-8')
        encrypted_semester = des_cipher.encrypt(semester.encode('utf-8'))
        semester = binascii.hexlify(encrypted_semester).decode('utf-8')
        print(encrypted_user)
        # if 
        student = Student.objects.get(username=encrypted_user)
        student_id = student.id
        courses = Record.objects.filter(student_id=student_id, year=year, semester=semester)
        decrypted_records = []
        for recod in courses:
            id= recod.id
                # Convert hexadecimal encrypted data to bytes
            code = binascii.unhexlify(recod.code)
            year = binascii.unhexlify(recod.year)
            semester = binascii.unhexlify(recod.semester)
            total = binascii.unhexlify(recod.total)
            grade = binascii.unhexlify(recod.grade)
            description = binascii.unhexlify(recod.description)
            lec = binascii.unhexlify(recod.lec_credits) 
            lab = binascii.unhexlify(recod.lab_credits)
            tut  = binascii.unhexlify(recod.tut_credits)

            # Decrypt the student details
            code = des_cipher.decrypt(code).decode('utf-8')
            year = des_cipher.decrypt(year).decode('utf-8')
            semester = des_cipher.decrypt(semester).decode('utf-8')
            total = des_cipher.decrypt(total).decode('utf-8')
            grade = des_cipher.decrypt(grade).decode('utf-8')
            description = des_cipher.decrypt(description).decode('utf-8')
            lec = des_cipher.decrypt(lec).decode('utf-8')
            lab = des_cipher.decrypt(lab).decode('utf-8')
            tut  = des_cipher.decrypt(tut).decode('utf-8')
            
            decrypted_record = {
                'id':id,
                'code': code,
                'year': year,
                'semester': semester,
                'total': total,
                'grade': grade,
                'description':description,
                'lec_credits':lec,
                'lab_credits':lab,
                'tut_credits':tut
            }
        
            decrypted_records.append(decrypted_record) 
        if len(courses) == 0:
            return render(request, 'goc_app/calculate_gp_user.html', {'record': None})
        else:
            try:
                decrypted_records = []
                for recod in courses:
                    id= recod.id
                        # Convert hexadecimal encrypted data to bytes
                    code = binascii.unhexlify(recod.code)
                    year = binascii.unhexlify(recod.year)
                    semester = binascii.unhexlify(recod.semester)
                    total = binascii.unhexlify(recod.total)
                    grade = binascii.unhexlify(recod.grade)
                    description = binascii.unhexlify(recod.description)
                    lec = binascii.unhexlify(recod.lec_credits) 
                    lab = binascii.unhexlify(recod.lab_credits)
                    tut  = binascii.unhexlify(recod.tut_credits)

                    # Decrypt the student details
                    code = des_cipher.decrypt(code).decode('utf-8')
                    year = des_cipher.decrypt(year).decode('utf-8')
                    semester = des_cipher.decrypt(semester).decode('utf-8')
                    total = des_cipher.decrypt(total).decode('utf-8')
                    grade = des_cipher.decrypt(grade).decode('utf-8')
                    description = des_cipher.decrypt(description).decode('utf-8')
                    lec = des_cipher.decrypt(lec).decode('utf-8')
                    lab = des_cipher.decrypt(lab).decode('utf-8')
                    tut  = des_cipher.decrypt(tut).decode('utf-8')
                    
                    decrypted_record = {
                        'id':id,
                        'code': code,
                        'year': year,
                        'semester': semester,
                        'total': total,
                        'grade': grade,
                        'description':description,
                        'lec_credits':lec,
                        'lab_credits':lab,
                        'tut_credits':tut
                    }        
                    decrypted_records.append(decrypted_record) 
                total_credits = sum(float(record['total']) for record in decrypted_records)
                print(total_credits)
                quality_sum = 0.0
                for course in decrypted_records:
                    grade_point = grade_points.get(course['grade'], 0.0)
                    quality_points = float(course['total']) * grade_point
                    quality_sum += quality_points
            
                points = quality_sum / total_credits
                gpa = round(points, 2)
                cgpa = round(points, 2)
                print(gpa)
                # Generate the hash using XOR of DES ciphertext blocks
                # Retrieve the private key from the database
                key_pair = RSAKeyPair.objects.latest('created_at')
                private_key = key_pair.private_key
                print(private_key)
                # Generate the digital signature
                message = f"GPA: {gpa}, CGPA: {cgpa}"
            
                # Generate the hash using XOR of DES ciphertext blocks
                des_key = b'SECRET01'
                cipher = DES.new(des_key, DES.MODE_ECB)
                ciphertext_blocks = []
                
                message_bytes = message.encode()
                padded_message = pad(message_bytes, DES.block_size)  # Pad the message to the block size
                
                for i in range(0, len(padded_message), DES.block_size):
                    block = padded_message[i:i+DES.block_size]
                    ciphertext = cipher.encrypt(block)
                    ciphertext_blocks.append(ciphertext)
                
                hash_value = ciphertext_blocks[0]
                
                for i in range(1, len(ciphertext_blocks)):
                    hash_value = bytes([a ^ b for a, b in zip(hash_value, ciphertext_blocks[i])])
                
                # Sign the hash value using the private key
                message_hash = SHA256.new(hash_value)
                private_key_rsa = RSA.import_key(private_key)
                signer = pkcs1_15.new(private_key_rsa)
                signature = signer.sign(message_hash)
                
                return render(request, 'goc_app/calculate_gp_user.html', {'record': decrypted_records, 'gpa': gpa, 'cgpa': cgpa, 'signature': signature, 'year':year, 'semester':semester})
            except Student.DoesNotExist:
                return HttpResponse('Student does not exist.')

    else:
        return HttpResponse('Invalid request method.')