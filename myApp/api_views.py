from rest_framework import generics

from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer



class HabitListAPIView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    

class HabitDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer