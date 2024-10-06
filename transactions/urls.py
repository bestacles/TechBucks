from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:student_id>/', views.add_transaction, name='add_transaction'),
    # Add other URL patterns as needed
]
