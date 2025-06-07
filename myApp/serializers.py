from rest_framework import serializers
from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Habit
        fields = ('id', 'name', 'target', 'is_complete',)
        
        
    
class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = HabitCompletion
        fields = ('id', 'habit', 'completed_date',)
        