from django.urls import path
from .views import (IndexView, HabitListView, HabitCreateView,
                    HabitUpdateView, HabitDeleteView, complete_habit,
                    habit_detail_view)

urlpatterns = [
    path('habit/<int:pk>/detail', habit_detail_view, name='habit_detail'),
    path('habit/<int:pk>/complete', complete_habit, name='habit_complete'),
    path('habit/<int:pk>/delete', HabitDeleteView.as_view(), name='habit_delete'),
    path('habit/<int:pk>/edit', HabitUpdateView.as_view(), name='habit_edit'),
    path('habit/habit_new', HabitCreateView.as_view(), name='habit_new'),
    path('habit/habit_list', HabitListView.as_view(), name='habit_list'),
    path('', IndexView.as_view(), name='home'),
]
