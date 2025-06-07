from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    path('habits/', api_views.HabitListAPIView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', api_views.HabitDetailAPIView.as_view(), name='habit-detail'),
    path('logs/', api_views.HabitLogListAPIView.as_view(), name='log-list'),
    path('logs/<int:pk>/', api_views.HabitLogDetailAPIView.as_view(), name='log-detail'),
    path('logs/<int:pk>/log-today/', api_views.LogTodayAPIView.as_view(), name='log-today'),
]