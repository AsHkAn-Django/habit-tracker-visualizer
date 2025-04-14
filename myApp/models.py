from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


# Create your models here.
class Habit(models.Model):
    """A class for creating a new habit"""
    name = models.CharField(max_length=260)
    target = models.IntegerField()
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('habit_list')


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    completed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_time = timezone.localtime(self.completed_date)
        return f"{self.habit} - {local_time}"
