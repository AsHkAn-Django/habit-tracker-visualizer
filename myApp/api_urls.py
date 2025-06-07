from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    path('habits/', api_views.HabitListAPIView.as_view(), name='habit-list'),
    path('habits/<int:pk>/', api_views.HabitDetailAPIView.as_view(), name='habit-detail'),
]