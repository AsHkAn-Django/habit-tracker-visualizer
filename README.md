# Habit Tracker Visualizer

Track your habits and visualize your progress with interactive charts. Built with Django and Chart.js, this project allows users to monitor habit completion on a daily, weekly, and monthly basis through dynamic data visualizations.

## Features

- User-friendly habit tracking interface
- Daily, weekly, and monthly habit completion stats
- Interactive charts using Chart.js
- JSON endpoints for real-time data visualization
- Responsive design with modern front-end integration

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Database:** SQLite (default, can be switched to PostgreSQL)

## Key Concepts

- Front-end data visualization
- Integration of JavaScript libraries with Django
- Dynamic rendering of data via API endpoints
- Clean separation of logic and presentation

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/habit-tracker-visualizer.git
   cd habit-tracker-visualizer

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python manage.py runserver
```

4. Visit http://localhost:8000 to start tracking your habits!


## Tutorial
Toggle between completed and uncompleted habit
```python
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
```
---

showing a chart with chart.js
```python
# prepare the data in the views.py
def chart_report(request, pk):
    considered_days = 120
    habit = get_object_or_404(Habit, pk=pk)
    completed_habits = HabitCompletion.objects.filter(habit=habit)
    daily_dates, daily_counts = get_daily_report(completed_habits, considered_days)
    
    context = {
        'habit': habit,
        'daily_dates': json.dumps(daily_dates),
        'daily_counts': json.dumps(daily_counts),     
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
```

```html
<!-- add this in your html file -->
<h2 class="text-center mb-4">Daily Chart - {{ habit.name }}</h2>
<div class="mb-5">
      <canvas id="dailyChart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

```js
// Add this to your js file or script tag

// Daily Chart
const dailyCtx = document.getElementById('dailyChart').getContext('2d');
const dailyChart = new Chart(dailyCtx, {
   type: 'bar',
   data: {
      labels: {{ daily_dates|safe }}, // PAY ATTENTION IN VIEWS WE USED JSON.DUMP AND IN HERE SAFE FUILTER SO MAKE THE DATA READABLE FOR JS.
      datasets: [{
            label: 'Daily Completions',
            data: {{ daily_counts|safe }},
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
      }]
   },
   options: {
      scales: {
            y: { beginAtZero: true }
      }
   }
});
```



## Contributing
Feel free to fork the repo and submit a pull request. All contributions are welcome!