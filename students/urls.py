# students/urls.py

from django.urls import path
from . import views
from rewards import views as reward_views
from rewards import views as rewards_views


app_name = 'students'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('scan/', views.scan_qr_code, name='scan_qr_code'),
    path('add/<student_id>/', views.add_points, name='add_points'),
    path('deduct/<student_id>/', views.deduct_points, name='deduct_points'),
    path('add_points_to_class/<homeroom>/', views.add_points_to_class, name='add_points_to_class'),
    path('update_points_for_class/<homeroom>/<int:points>/', views.update_points_for_class, name='update_points_for_class'),
    path('update_points/<student_id>/', views.update_points, name='update_points'),
    path('classes/', views.class_list, name='class_list'),  # New class list URL
    path('class/<homeroom>/', views.class_profile, name='class_profile'),
    path('update_class_points/<homeroom>/', views.update_class_points, name='update_class_points'),
    path('<int:student_id>/', views.student_profile, name='student_profile'),
    path('add_transaction/<int:student_id>/', views.add_transaction, name='add_transaction'),  # Add transaction
    path('<int:student_id>/', views.student_profile, name='student_profile'),  # Ensure this is correct
    path('redeem/<str:student_id>/<int:reward_id>/', reward_views.redeem_reward, name='redeem_reward'),  # Updated this line
    path('students/generate-id-cards/', views.generate_student_id_cards, name='generate_student_id_cards'),
    path('pdf-status/', views.pdf_generation_status, name='pdf_generation_status'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]
]
