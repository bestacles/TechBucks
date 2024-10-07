from django.contrib import admin
from .models import Reward, Redemption

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'category', 'unique_id')

class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'reward', 'redeemed_at')
    list_filter = ('redeemed_at',)
    search_fields = ('student__first_name', 'student__last_name', 'reward__name')