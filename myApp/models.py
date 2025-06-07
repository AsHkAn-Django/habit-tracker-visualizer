from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.conf import settings



class Habit(models.Model):
    """A class for creating a new habit"""
    name = models.CharField(max_length=260)
    target = models.IntegerField()
    is_complete = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('habit_list')


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='habits')
    completed_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_habits')

    def __str__(self):
        local_time = timezone.localtime(self.completed_date)
        return f"{self.habit} - {local_time}"
