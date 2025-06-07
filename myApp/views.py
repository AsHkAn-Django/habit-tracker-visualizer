from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

from .models import Habit, HabitCompletion
from .forms import HabitForm

from datetime import timedelta
from dateutil.relativedelta import relativedelta
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
    """Get the daily, weekly and monthly data for the charts."""
    considered_days = 120
    considered_weeks = 17
    considered_months = 4
    habit = get_object_or_404(Habit, pk=pk)
    completed_habits = HabitCompletion.objects.filter(habit=habit)
    daily_dates, daily_counts = get_daily_report(completed_habits, considered_days)
    weekly_dates, weekly_counts = get_weekly_report(completed_habits, considered_weeks)
    monthly_dates, monthly_counts = get_monthly_report(completed_habits, considered_months)
    
    context = {
        'habit': habit,
        'daily_dates': json.dumps(daily_dates),
        'daily_counts': json.dumps(daily_counts),     
        'weekly_dates': json.dumps(weekly_dates),     
        'weekly_counts': json.dumps(weekly_counts),     
        'monthly_dates': json.dumps(monthly_dates),
        'monthly_counts': json.dumps(monthly_counts),
    }
    return render(request, 'myApp/chart_report.html', context)



def get_daily_report(habits, days):
    """Prepare counts, and dates for daily chart."""
    # start and end dates 
    start_date = (timezone.now() - timedelta(days=days)).date()
    end_date = timezone.now().date()
    
    # Aggregate completions per day from the database
    daily_tasks_qs = (
        # select the habits that are greater than start_date
        habits.filter(completed_date__date__gte=start_date)
        # create a new filed name 'day' and then attach the completed_date to it
        .annotate(day=TruncDay('completed_date'))
        # group all the habits in that day
        .values('day')
        # count the number of ids in that group and add a field name task_count and attach that number to it
        .annotate(task_count=Count('id'))
        # order them by day(the field that we just made)
        .order_by('day')
    )
    
    # Create a dictionary (1999-01-01: 5)
    tasks_dict = {
        entry['day'].strftime('%Y-%m-%d'): entry['task_count'] for entry in daily_tasks_qs
    }
    
    # Generate full lists for every day in the period with zero for missing days
    all_dates = []
    all_counts = []
    current_date = start_date
    while current_date <= end_date:
        # Reformat today's date to the same format that we have in our tasks_dict dictionairy
        date_str = current_date.strftime('%Y-%m-%d')
        # now add them to the list of dates
        all_dates.append(date_str)
        # Add the number of tasks to the all_counts and iff the day is missing in tasks_dict, default to 0
        all_counts.append(tasks_dict.get(date_str, 0))
        # go to next day
        current_date += timedelta(days=1)
    
    return all_dates, all_counts


def get_weekly_report(habits, weeks):
    """Prepare counts, and dates for weekly chart."""

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
    current_week = start_date
    while current_week <= timezone.now().date():
        week_str = current_week.strftime('%Y-%m-%d')
        weeks_list.append(week_str)
        counts_list.append(tasks_dict.get(week_str, 0))
        current_week += timedelta(weeks=1)
    
    return weeks_list, counts_list


def get_monthly_report(habits, months):
    """Prepare counts, and dates for monthly chart."""

    # Start date (N months ago)
    start_date = (timezone.now() - relativedelta(months=months)).date()
    end_date = timezone.now().date()

    # Query completions grouped by month
    monthly_tasks_qs = (
        habits.filter(completed_date__date__gte=start_date)
        .annotate(month=TruncMonth('completed_date'))
        .values('month')
        .annotate(task_count=Count('id'))
        .order_by('month')
    )

    # Dict of month: count
    tasks_dict = {
        entry['month'].strftime('%Y-%m'): entry['task_count']
        for entry in monthly_tasks_qs
    }

    # Generate list of months and fill counts
    months_list = []
    counts_list = []

    current = start_date.replace(day=1)
    while current <= end_date:
        month_str = current.strftime('%Y-%m')
        months_list.append(month_str)
        counts_list.append(tasks_dict.get(month_str, 0))
        current += relativedelta(months=1)
        
    return months_list, counts_list