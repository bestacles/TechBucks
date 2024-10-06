from django.urls import path
from . import views

app_name = 'rewards'  # This is necessary to use the namespace

urlpatterns = [
    path('', views.reward_list, name='reward_list'),
    path('redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    path('error/', views.error_page, name='error_page'),
]
