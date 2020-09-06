# позволяет узнать ссылку на URL по его имени, параметр name функции path
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm
from django.core.mail import send_mail



class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "users/reg.html"
