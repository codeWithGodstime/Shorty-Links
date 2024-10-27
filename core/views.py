from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import TemplateView, View, FormView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate

from .models import CustomUserModel, UrlModel


class HomepageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['links'] = UrlModel.objects.filter(session_key = self.request.session.session_key)
        context['attempts'] = UrlModel.get_remaining_limit(self.request.session.session_key)
        return context


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') # TODO: change to email later
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            messages.info(request, "Loggedin successfully!")
            return redirect('dashboard')
            

    return render(request, 'registration/login.html')

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUserModel
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class RegistrationView(FormView):
    template_name = 'registration/signup.html'
    success_url = '/login'
    form_class = RegistrationForm


class DashboardView(LoginRequiredMixin, ListView):
    model = UrlModel
    template_name = 'dashboard.html'
    context_object_name = 'links'

    def get_queryset(self):
        queryset = UrlModel.objects.filter(user = self.request.user)
        return queryset 

class UrlUpdateView(LoginRequiredMixin, UpdateView):
    model = UrlModel
    fields = ['original_link']

    def form_valid(self, form):
        rs = super().form_valid(form)
        
        return rs


def shorten(request):
    """ get the request.session and increase the shorten link attempts  """

    if request.method == 'POST':
        link = request.POST.get('url')

        if not request.user.is_authenticated:
            # check if limit has been reached 
            session_id = request.session.session_key
            link_count = UrlModel.check_max_limit_for_anon_users(session_id)

            if link_count:
                messages.error(request, 'Reached max limit')
        else:
            # for anonymous users 
            url = UrlModel.objects.create(
                session_key = request.session.session_key,
                original_link  = link
                )
            url.save()
            attempts = request.session.get('attempts', 0)

            if attempts:
                attempts += 1

                messages.success(request, 'link shortening done successfully')
            
        url = UrlModel.objects.create(original_link=link, user=request.user)
        url.save()

        return redirect('/')

    
    return messages.error(request, 'Something occur, please try again')


def visit(request, code):
    link = get_object_or_404(UrlModel, unique_code=code)

    link.clicks += 1
    link.save()
    return redirect(link.original_link)
    

"""
    when any event happens on the UrlModel, create, delete, update by the request user, send notification to user
"""

# https://medium.com/@devsumitg/revolutionize-your-user-experience-creating-real-time-notifications-with-django-channels-18053b958fb6