from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Habit, HabitCompletion
from django.utils import timezone

User = get_user_model()


class HabitAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(name='Drink water', target=1, user=self.user)

    def test_create_habit(self):
        url = reverse('api:habit-list')
        data = {'name': 'Exercise', 'target': 2, 'is_complete': False}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_habits(self):
        url = reverse('api:habit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_habit(self):
        url = reverse('api:habit-detail', args=[self.habit.pk])
        response = self.client.patch(url, {'name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated')

    def test_delete_habit(self):
        url = reverse("api:habit-detail", args=[self.habit.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_log_today_success(self):
        url = reverse('api:log-today', args=[self.habit.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('habit logged successfully', response.data['detail'].lower())

    def test_log_today_duplicate(self):
        HabitCompletion.objects.create(habit=self.habit, user=self.user, completed_date=timezone.now())
        url = reverse('api:log-today', args=[self.habit.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already logged today', response.data['detail'].lower())

