from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model



class UserCreateView(generic.CreateView):
    model = get_user_model()
    template_name = "users/signup.html"
    success_url = reverse_lazy('users:login')
    form_class = UserCreationForm
