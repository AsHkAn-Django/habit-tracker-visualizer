from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils.dateparse import parse_date


from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer



class HabitListAPIView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    

class HabitDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    
    
class HabitLogListAPIView(generics.ListCreateAPIView):
    """
    List of logs( use GET /logs/?start=2024-01-01&end=2024-02-01 for getting filtered date.)
    """
    serializer_class = HabitCompletionSerializer
    
    def get_queryset(self):
        qs = HabitCompletion.objects.prefetch_related('habit')
        start = self.request.query_params.get('start')
        end =  self.request.query_params.get('end')
        
        if start and end:
            # we use pars_date here to convert the usl string to date format
            return qs.filter(completed_date__range=[parse_date(start), parse_date(end)])
        return qs
        
    
    
class HabitLogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HabitCompletion.objects.prefetch_related('habit')
    serializer_class = HabitCompletionSerializer
    

class LogTodayAPIView(APIView):
    """
    Create a log with just sending a post request the the habit url.
    """
    def post(self, request, pk):
        habit = get_object_or_404(Habit, pk=pk)
        
        if HabitCompletion.objects.filter(habit=habit, completed_date__date=timezone.now().date()).exists():
            return Response({'detail': 'Already logged today.'}, status=status.HTTP_400_BAD_REQUEST)
        
        HabitCompletion.objects.create(habit=habit)
        return Response({'detail': 'Habit logged successfully!'}, status=status.HTTP_201_CREATED)
        
    
