from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('', views.reward_list, name='reward_list'),
    path('redeem/<str:student_id>/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),  # Updated this line
    path('error/', views.error_page, name='error_page'),
    path('add-reward/', views.add_reward_view, name='add_reward'),
    path('success/', views.success, name='rewards_success'),
]
