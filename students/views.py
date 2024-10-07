import logging  # Import the logging module
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Student
from transactions.models import Transaction
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
import qrcode
from transactions.forms import TransactionForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from rewards.models import Reward
from transactions.models import Transaction
from django.contrib.auth.forms import UserCreationForm, logger
from django.contrib.auth import login
from django.contrib import messages


# Helper function to check if the user is a teacher
def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def main_page(request):
    # Get query parameters for filtering
    grade = request.GET.get('grade')
    homeroom = request.GET.get('homeroom')
    teacher = request.GET.get('teacher')

    # Filter students based on the selected filters
    students = Student.objects.all()
    if grade:
        students = students.filter(grade=grade)
    if homeroom:
        students = students.filter(homeroom=homeroom)
    if teacher:
        students = students.filter(homeroom_teacher=teacher)

    # Get unique values for filters
    grades = students.values_list('grade', flat=True).distinct()
    homerooms = students.values_list('homeroom', flat=True).distinct()
    teachers = students.values_list('homeroom_teacher', flat=True).distinct()

    # Calculate total TechBucks for each class
    classes_with_totals = students.values('homeroom', 'homeroom_teacher').annotate(
        total_techbucks=Sum('transactions__amount')
    ).distinct()

    # Calculate total students and classes
    total_students = students.count()
    classes_with_totals = students.values('homeroom', 'homeroom_teacher').annotate(
        total_techbucks=Sum('transactions__amount')
    )

    # Calculate total TechBucks for all students
    total_techbucks = students.aggregate(Sum('transactions__amount'))['transactions__amount__sum'] or 0

    return render(request, 'students/main_page.html', {
        'students': students,
        'grades': grades,
        'homerooms': homerooms,
        'teachers': teachers,
        'total_techbucks': total_techbucks,
        'classes_with_totals': classes_with_totals,
    })

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import Student
from transactions.models import Transaction  # Assuming you track transactions
from rewards.models import Reward

def student_profile(request, student_id):
    # Fetch student information
    student = get_object_or_404(Student, student_id=str(student_id))

    # Fetch transactions for the student
    transactions = Transaction.objects.filter(student=student).order_by('-timestamp')

    # Calculate total TechBucks
    total_techbucks = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    # Define the list of amounts
    amounts = [5, 10, 25, 50, 100]

    # Check if the user is a teacher
    is_teacher = request.user.groups.filter(name='Teacher').exists()

    logger.debug(f"Rendering student profile for student ID: {student.id}")

    context = {
        'student': student,
        'transactions': transactions,
        'total_techbucks': total_techbucks,
        'amounts': amounts,  # Include the amounts list in the context
        'is_teacher': is_teacher,  # Pass whether the user is a teacher
        'rewards': Reward.objects.all(),  # Pass the rewards to the template

    }

    return render(request, 'students/student_profile.html', context)

def scan_qr_code(request):
    # This view will redirect based on the student ID input
    student_id = request.GET.get('student_id')
    if student_id:
        return redirect('students:add_transaction', student_id=student_id)
    return render(request, 'students/scan_qr_code.html')

# Only teachers can add points
@user_passes_test(is_teacher)
def add_points(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        # Create the transaction and save the current user as the one who performed it
        Transaction.objects.create(
            student=student,
            amount=points,
            description='Points Added',
            performed_by=request.user  # Store the teacher/user who performed the action
        )
        return redirect('students:student_profile', student_id=student_id)
    return render(request, 'students/add_points.html', {'student': student})

# Only teachers can deduct points
@user_passes_test(is_teacher)
def deduct_points(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        # Create the transaction and save the current user as the one who performed it
        Transaction.objects.create(
            student=student,
            amount=-points,
            description='Points Deducted',
            performed_by=request.user  # Store the teacher/user who performed the action
        )
        return redirect('students:student_profile', student_id=student_id)
    return render(request, 'students/deduct_points.html', {'student': student})

def add_points_to_class(request, homeroom):
    students = Student.objects.filter(homeroom=homeroom)
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        for student in students:
            Transaction.objects.create(student=student, amount=points, description='Class Points Added')
        return redirect('students:class_profile', homeroom=homeroom)
    return render(request, 'students/add_points_to_class.html', {'students': students})


@login_required
def update_points_for_class(request, homeroom, points):
    students = Student.objects.filter(homeroom=homeroom)
    description = request.POST.get('description', 'Class TechBucks Update')  # Get description from form

    # Loop through each student and create a transaction for them
    for student in students:
        Transaction.objects.create(
            student=student,
            amount=points,
            description=description,
            performed_by=request.user  # Track the teacher/user who is performing the transaction
        )

    return JsonResponse({'status': 'success', 'homeroom': homeroom})


def update_points(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, student_id=str(student_id))
        points = int(request.POST.get('points', 0))
        description = request.POST.get('description', 'Points update')

        # Create a new transaction
        Transaction.objects.create(
            student=student,
            amount=points,  # This will be negative for deductions
            description=description,
            performed_by=request.user
        )

        # Update the student's total TechBucks
        #student.techbucks += points
       # student.save()

        messages.success(request, f"{'Added' if points > 0 else 'Deducted'} {abs(points)} TechBucks.")
        return redirect('students:student_profile', student_id=student.student_id)


def class_profile(request, homeroom):
    # Fetch class information
    students = Student.objects.filter(homeroom=homeroom)

    # Calculate total TechBucks for the class
    total_class_techbucks = sum(student.total_techbucks() for student in students)

    # Fetch class transactions based on the student's homeroom
    class_transactions = Transaction.objects.filter(student__homeroom=homeroom).order_by('-timestamp')

    # Generate the QR code URL
    class_qr_code_url = generate_class_qr_code(homeroom)

    # Get the first student to access grade and homeroom_teacher
    first_student = students.first()
    # Check if the user is a teacher
    is_teacher = request.user.groups.filter(name='Teacher').exists()


    context = {
        'homeroom': homeroom,
        'grade': first_student.grade if students.exists() else '',
        'teacher': first_student.homeroom_teacher if students.exists() else '',
        'class_qr_code_url': class_qr_code_url,  # Pass the generated QR code URL
        'total_class_techbucks': total_class_techbucks,
        'students': students,
        'class_transactions': class_transactions,
        'amounts': [5, 10, 25, 50, 100],
        'is_teacher': is_teacher,  # Pass whether the user is a teacher
    }

    return render(request, 'students/class_profile.html', context)


@login_required
def update_class_points(request, homeroom):
    students = Student.objects.filter(homeroom=homeroom)

    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        description = request.POST.get('description', 'Class Points Update')  # Get description from form

        for student in students:
            Transaction.objects.create(
                student=student,
                amount=points,
                description=description,
                performed_by=request.user  # Track the user performing the transaction
            )

    return redirect('students:class_profile', homeroom=homeroom)


# Registration view with default student group assignment
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print("Form is valid and user saved.")

            # Assign user to the Student group by default
            student_group, created = Group.objects.get_or_create(name='Student')
            if created:
                print("Student group was created.")
            student_group.user_set.add(user)
            print(f"User {user.username} added to Student group.")

            login(request, user)
            return redirect('students:main_page')  # Redirect to main page or wherever
        else:
            print("Form is not valid.")
            print(form.errors)  # Print form errors for debugging
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def generate_class_qr_code(homeroom):
    # Generate the QR code content
    qr_content = f"Class:{homeroom}"
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill="black", back_color="white")

    # Save the image to a buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Save the image to a file in the media directory
    filename = f"qr_codes/classes/{homeroom}.png"
    file_path = default_storage.save(filename, ContentFile(buffer.getvalue()))

    # Return the URL for the saved QR code image
    return default_storage.url(file_path)

def add_transaction(request, student_id=None):
    student = get_object_or_404(Student, student_id=student_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            is_class_transaction = form.cleaned_data.get('is_class_transaction')
            amount = form.cleaned_data.get('amount')  # Get the transaction amount
            description = form.cleaned_data.get('description')  # Get the description

            # If it's a class transaction, apply the transaction to all students in the homeroom
            if is_class_transaction:
                homeroom = student.homeroom
                students_in_class = Student.objects.filter(homeroom=homeroom)
                for class_student in students_in_class:
                    # Create a separate transaction for each student in the class
                    Transaction.objects.create(
                        student=class_student,
                        amount=amount,
                        description=f"Class Transaction: {description}"
                    )
            else:
                # Apply the transaction to the individual student
                transaction = form.save(commit=False)
                transaction.student = student
                transaction.save()

            # Redirect to the student's profile after the transaction
            return redirect('students:student_profile', student_id=student.student_id)

    else:
        form = TransactionForm(initial={'student': student})

    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'student': student,
    })

def class_list(request):
    classes_with_teachers = Student.objects.values('homeroom', 'homeroom_teacher', 'grade').annotate(
        total_techbucks=Sum('transactions__amount')
    )

    total_school_techbucks = Student.objects.aggregate(total_techbucks=Sum('transactions__amount'))['total_techbucks'] or 0

    context = {
        'classes_with_teachers': classes_with_teachers,
        'total_school_techbucks': total_school_techbucks
    }

    return render(request, 'students/class_list.html', context)
