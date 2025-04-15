from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Habit, HabitCompletion
from .forms import HabitForm
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncWeek
from django.db.models import Count
import json


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
    """ Get the list of the list of the dates and completion task for a specific period."""
    considered_days = 5
    habit = get_object_or_404(Habit, pk=pk)
    completed_habits = HabitCompletion.objects.filter(habit=habit)
    last_seven_days = timezone.now() - timedelta(days=considered_days)
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


def chart_report(request, pk):
    considered_days = 120
    considered_weeks = 17
    considered_months = 105
    habit = get_object_or_404(Habit, pk=pk)
    completed_habits = HabitCompletion.objects.filter(habit=habit)
    daily_dates, daily_counts = get_daily_report(completed_habits, considered_days)
    weekly_dates, weekly_counts = get_weekly_report(completed_habits, considered_weeks)

    context = {
        'habit': habit,
        'daily_dates': json.dumps(daily_dates),
        'daily_counts': json.dumps(daily_counts),     
        'weekly_dates': json.dumps(weekly_dates),     
        'weekly_counts': json.dumps(weekly_counts),     

    }
    return render(request, 'myApp/chart_report.html', context)



def get_daily_report(habits, days):
    # start and end dates 
    start_date = (timezone.now() - timedelta(days=days)).date()
    end_date = timezone.now().date()
    
    # Aggregate completions per day from the database
    daily_tasks_qs = (
        habits.filter(completed_date__date__gte=start_date)
        .annotate(day=TruncDay('completed_date'))
        .values('day')
        .annotate(task_count=Count('id'))
        .order_by('day')
    )
    
    # Create a dictionary mapping date (as a string) to its task count
    tasks_dict = {
        entry['day'].strftime('%Y-%m-%d'): entry['task_count'] for entry in daily_tasks_qs
    }
    
    # Generate full lists for every day in the period with zero for missing days
    all_dates = []
    all_counts = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        all_dates.append(date_str)
        # If the day is missing in tasks_dict, default to 0
        all_counts.append(tasks_dict.get(date_str, 0))
        current_date += timedelta(days=1)
    
    return all_dates, all_counts

def get_weekly_report(habits, weeks):
    # assumed considered_weeks is the number of weeks you want to look back
    start_date = (timezone.now() - timedelta(weeks=weeks)).date()

    # Align start_date to the Monday of that week
    start_date -= timedelta(days=start_date.weekday())
    
    # Aggregate by week (e.g., each week's Monday)
    weekly_tasks_qs = (
        habits.filter(completed_date__date__gte=start_date)
        .annotate(week=TruncWeek('completed_date'))
        .values('week')
        .annotate(task_count=Count('id'))
        .order_by('week')
    )
    # Build the dictionary: formatted week -> count
    tasks_dict = {
        entry['week'].strftime('%Y-%m-%d'): entry['task_count']
        for entry in weekly_tasks_qs
    }
        
    # Generate a list of weeks. One strategy is to iterate week by week.
    weeks_list = []
    counts_list = []
    
    # Start from the truncated start date (make sure it is aligned to week boundaries if needed)
    # For simplicity, this example uses 7-day intervals.
    current_week = start_date
    while current_week <= timezone.now().date():
        week_str = current_week.strftime('%Y-%m-%d')
        weeks_list.append(week_str)
        counts_list.append(tasks_dict.get(week_str, 0))
        current_week += timedelta(weeks=1)
    
    print(counts_list)
    return weeks_list, counts_list