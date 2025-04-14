from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Habit, HabitCompletion
from .forms import HabitForm
from django.utils import timezone
from datetime import timedelta


# Create your views here.
class IndexView(TemplateView):
    template_name = 'myApp/index.html'


class HabitListView(ListView):
    model = Habit
    context_object_name = 'habits'
    template_name = 'myApp/habit_list.html'


class HabitCreateView(CreateView):
    model = Habit
    form_class = HabitForm
    template_name = 'myApp/habit_new.html'
    success_url = 'habit_list'


class HabitUpdateView(UpdateView):
    model = Habit
    template_name = 'myApp/habit_edit.html'
    form_class = HabitForm


class HabitDeleteView(DeleteView):
    model = Habit
    template_name = 'myApp/habit_delete.html'
    success_url = reverse_lazy('habit_list')


def complete_habit(request, pk):
    """Checks if the habit is completed or not."""
    habit = get_object_or_404(Habit, pk=pk)
    if habit.is_complete:
        habit.is_complete = False
    else:
        habit.is_complete = True
        habit_completed = HabitCompletion(
            habit=habit
        )
        habit_completed.save()
    habit.save()
    return redirect('habit_list')


def habit_detail_view(request, pk):
    """ Get the list of the dates for a habit and the percentage in the last 7days."""
    habit = get_object_or_404(Habit, pk=pk)
    completed_habits = HabitCompletion.objects.filter(habit=habit)

    last_seven_days = timezone.now() - timedelta(days=7)

    recent_completion = completed_habits.filter(completed_date__gte=last_seven_days)
    counted_habits = recent_completion.count()
    if habit.target:
        percentage = int((counted_habits / habit.target) * 100)
    else:
        percentage = 0

    context = {
        'habit': habit,
        'completed_habits': completed_habits,
        'percentage': percentage,
    }
    return render(request, 'myApp/habit_detail.html', context)
