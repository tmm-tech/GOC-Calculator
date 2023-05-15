from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group,Permission

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # staff = models.OneToOneField('Staff', on_delete=models.CASCADE, null=True, blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150, unique=True)
    groups = models.ManyToManyField(Group, related_name='User')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['lastname', 'firstname', 'username']
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='permission_users',
        help_text=(
            'Specific permissions for this user.'
            'A user will get all permissions granted to each of their groups.'
            'Additionally, a user will get all permissions granted to their '
            'user level (either globally or for the current app).'
        ),
        related_query_name='permission_user',
    )
    objects = UserManager()

class Staff(AbstractBaseUser, PermissionsMixin):
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='Staff')
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150)
    groups = models.ManyToManyField(Group, related_name='Staff')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('staff permissions'),
        blank=True,
        related_name='permission_staff',
        help_text=(
            'Specific permissions for this user.'
            'A user will get all permissions granted to each of their groups.'
            'Additionally, a user will get all permissions granted to their '
            'user level (either globally or for the current app).'
        ),
        related_query_name='permission_staff',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['lastname', 'firstname', 'username']
    
    objects = UserManager()

class Student(AbstractBaseUser, PermissionsMixin):
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150, unique=True)
    groups = models.ManyToManyField(Group, related_name='students')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('student permissions'),
        blank=True,
        related_name='permission_student',
        help_text=(
            'Specific permissions for this user.'
            'A user will get all permissions granted to each of their groups.'
            'Additionally, a user will get all permissions granted to their '
            'user level (either globally or for the current app).'
        ),
        related_query_name='permission_student',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['lastname', 'firstname', 'username']

    objects = UserManager()
    def __str__(self):
        return self.name

    def calculate_gpa(self, semester):
        """
        Calculate GPA for a given semester
        """
        grades = {'A': 5.00, 'B': 4.00, 'C': 3.00, 'D': 2.00, 'E': 1.00, 'F': 0.00}
        total_grade_point = 0
        total_course_unit = 0

        # Calculate total grade point and total course unit
        for record in CalculateGp.objects.filter(student=self, course__semester=semester):
            total_grade_point += grades.get(record.course_grade, 0) * record.course_unit
            total_course_unit += record.course_unit

        # Calculate GPA
        gpa = round(total_grade_point / total_course_unit, 2) if total_course_unit > 0 else 0

        return gpa

class Sysadmin(AbstractBaseUser, PermissionsMixin):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_superuser = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150, unique=True)
    groups = models.ManyToManyField(Group, related_name='Sysadmin')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='permission_sysadmin',
        help_text=(
            'Specific permissions for this user.'
            'A user will get all permissions granted to each of their groups.'
            'Additionally, a user will get all permissions granted to their '
            'user level (either globally or for the current app).'
        ),
        related_query_name='permission_sysadmin',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name', 'username']

    objects = UserManager()

class Record(models.Model):
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=5, decimal_places=2)
    tut_credits = models.DecimalField(max_digits=5, decimal_places=2)
    lec_credits = models.DecimalField(max_digits=5, decimal_places=2)
    lab_credits = models.DecimalField(max_digits=5, decimal_places=2)
    semester = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    student_id = models.IntegerField()

class SecretKey(models.Model):
    key = models.BinaryField()

class RSAKey(models.Model):
    public_key = models.BinaryField()
    private_key = models.BinaryField()

class Semester(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CalculateGp(models.Model):
    course_code = models.CharField(max_length=20)
    course_title = models.CharField(max_length=100)
    course_unit = models.PositiveIntegerField()
    course_grade = models.CharField(max_length=2)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_code} - {self.student}"

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically calculate the student's GPA and CGPA
        """
        super().save(*args, **kwargs)

        grades = {'A': 5.00, 'B': 4.00, 'C': 3.00, 'D': 2.00, 'E': 1.00, 'F': 0.00}
        total_grade_point = 0
        total_course_unit = 0

        # Calculate total grade point and total course unit
        for record in CalculateGp.objects.filter(student=self.student):
            total_grade_point += grades.get(record.course_grade, 0) * record.course_unit
            total_course_unit += record.course_unit

        # Calculate GPA and CGPA
        gpa = round(total_grade_point / total_course_unit, 2) if total_course_unit > 0 else 0
        cgpa = round((self.student.cgpa * self.student.total_course_unit + gpa * self.course_unit) / 
                     (self.student.total_course_unit + self.course_unit), 2) if self.student.total_course_unit > 0 else gpa

        # Update the student's GPA and CGPA
        self.student.gpa = gpa
        self.student.cgpa = cgpa
        self.student.total_course_unit += self.course_unit
        self.student.save()

class Course(models.Model):
    course_code = models.CharField(max_length=10, primary_key=True)
    course_title = models.CharField(max_length=100)

    def __str__(self):
        return self.title