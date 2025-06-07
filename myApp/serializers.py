from rest_framework import serializers
from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Habit
        fields = ('id', 'name', 'target', 'is_complete', 'user')
        read_only_fileds = ('user',)
        
        
    
class HabitCompletionSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    class Meta: 
        model = HabitCompletion
        fields = ('id', 'completed_date', 'habit', 'user')
        read_only_fields = ('user',)
        