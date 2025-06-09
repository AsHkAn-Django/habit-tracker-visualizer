from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from rest_framework import permissions

from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer
from .permissions import IsOwner


class HabitListAPIView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)



class HabitLogListAPIView(generics.ListCreateAPIView):
    """
    List of logs( use GET /logs/?start=2024-01-01&end=2024-02-01 for getting filtered date.)
    """
    serializer_class = HabitCompletionSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        qs = HabitCompletion.objects.filter(user=self.request.user).prefetch_related('habit')
        start = self.request.query_params.get('start')
        end =  self.request.query_params.get('end')

        if start and end:
            # we use pars_date here to convert the usl string to date format
            return qs.filter(completed_date__range=[parse_date(start), parse_date(end)])
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitLogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitCompletionSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return HabitCompletion.objects.filter(user=self.request.user).prefetch_related('habit')


class LogTodayAPIView(APIView):
    """
    Create a log with just sending a post request the the habit url.
    """
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    def post(self, request, pk):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        if HabitCompletion.objects.filter(habit=habit, completed_date__date=timezone.now().date()).exists():
            return Response({'detail': 'Already logged today.'}, status=status.HTTP_400_BAD_REQUEST)

        HabitCompletion.objects.create(habit=habit, user=request.user)
        return Response({'detail': 'Habit logged successfully!'}, status=status.HTTP_201_CREATED)


