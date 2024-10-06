from django.shortcuts import render, get_object_or_404, redirect
from .models import Reward, Redemption
from students.models import Student  # Assuming you track points through Student
from django.contrib import messages
from django.db import transaction  # For atomic operations
from django.core.exceptions import ObjectDoesNotExist

# View to handle reward redemption
@transaction.atomic  # Ensures all operations are successful or none are
def redeem_reward(request, reward_id):
    try:
        student = request.user.student  # Attempt to retrieve the student object
    except ObjectDoesNotExist:
        # Handle case where the user does not have an associated student
        messages.error(request, "You do not have an associated student profile.")
        return redirect('rewards:error_page')  # Redirect to error page

    # Proceed with reward redemption logic
    reward = get_object_or_404(Reward, id=reward_id)

    if student.points >= reward.cost:
        student.points -= reward.cost
        student.save()

        # Log the redemption
        Redemption.objects.create(student=student, reward=reward)
        messages.success(request, f"Successfully redeemed {reward.name}!")
    else:
        messages.error(request, "You do not have enough points to redeem this reward.")

    return redirect('rewards:reward_list')


from django.shortcuts import render
from .models import Reward
def create_reward(request):
    if request.method == 'POST':
        # Process your reward form here
        reward = Reward.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            cost=request.POST['cost']
        )
        reward.generate_qr_code()  # Call to generate and save QR code

        messages.success(request, "Reward created successfully!")
        return redirect('rewards:reward_list')
    return render(request, 'rewards/reward_form.html')


def reward_list(request):
    rewards = Reward.objects.all()
    return render(request, 'rewards/reward_list.html', {'rewards': rewards})



# Error page view
def error_page(request):
    return render(request, 'rewards/error_page.html')  # Simple error page
