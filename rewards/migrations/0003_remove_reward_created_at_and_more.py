# Generated by Django 5.1.1 on 2024-10-06 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0002_redemption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reward',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='reward',
            name='points_required',
        ),
        migrations.RemoveField(
            model_name='reward',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='reward',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='reward',
            name='cost',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reward',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='reward_qr_codes/'),
        ),
        migrations.AddField(
            model_name='reward',
            name='unique_id',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='reward',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
