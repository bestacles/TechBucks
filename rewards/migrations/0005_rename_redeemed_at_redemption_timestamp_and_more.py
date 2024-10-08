# Generated by Django 5.1.1 on 2024-10-07 02:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0004_alter_reward_unique_id'),
        ('students', '0006_remove_student_techbucks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='redemption',
            old_name='redeemed_at',
            new_name='timestamp',
        ),
        migrations.AlterField(
            model_name='redemption',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student'),
        ),
    ]
