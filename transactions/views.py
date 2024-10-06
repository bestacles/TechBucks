from django.shortcuts import render, get_object_or_404, redirect
from students.models import Student
from .forms import TransactionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def add_transaction(request, student_id=None):
    print("Reached add_transaction view.")  # Check if this line is executed
    student = get_object_or_404(Student, student_id=student_id)
    print(f"Student found: {student.first_name} {student.last_name}")

    if request.method == 'POST':
        print("Form method is POST.")  # Ensure that the form is being submitted
        form = TransactionForm(request.POST)
        if form.is_valid():
            print("Form is valid.")  # Check if form validation passes
            is_class_transaction = form.cleaned_data.get('is_class_transaction')
            amount = form.cleaned_data.get('amount')
            description = form.cleaned_data.get('description')

            print(f"Transaction details - Amount: {amount}, Description: {description}, Is Class Transaction: {is_class_transaction}")

            # Check if it's a class transaction
            if is_class_transaction:
                print("Processing class transaction...")
                homeroom = student.homeroom
                students_in_class = Student.objects.filter(homeroom=homeroom)
                for class_student in students_in_class:
                    Transaction.objects.create(
                        student=class_student,
                        amount=amount,
                        description=f"Class Transaction: {description}",
                        performed_by=request.user  # Add performed_by here
                    )
            else:
                # Apply transaction to the individual student
                print("Processing individual transaction...")
                Transaction.objects.create(
                    student=student,
                    amount=amount,
                    description=description,
                    performed_by=request.user  # Add performed_by here
                )

            # Redirect after form submission
            return redirect('students:student_profile', student_id=student.student_id)
        else:
            print("Form is not valid:", form.errors)  # Check form errors if validation fails
    else:
        print("GET request detected, rendering form.")
        form = TransactionForm(initial={'student': student})

    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'student': student,
    })





def update_points(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        description = request.POST.get('description', 'Point update')  # Get the description, default to 'Point update'

        # Create a new transaction and track who performed the action
        Transaction.objects.create(
            student=student,
            amount=points,
            description=description,
            performed_by=request.user  # Track the teacher/user who performed the transaction
        )

        return redirect('students:student_profile', student_id=student_id)
    return render(request, 'students/student_profile.html', {'student': student})

