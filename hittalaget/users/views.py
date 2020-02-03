from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    RedirectView,
    UpdateView,
)
from .forms import CreateUserForm, UpdateUserForm
from hittalaget.conversations.forms import PmMessageForm

User = get_user_model()


'''
Next iteration:
- Make sure dispatch/get_object are done correctly
- go over every view to make sure it meet the standard
- when no teams -- show same message as players when there are no player
- change password -- create your own view instead of using admin
- add the default image... and add it to the profile..
- use mixins?
- divide mixins and views "graphically" like other views..
- perhaps add age as visable for birthday..
- think about how to incorporate height..
'''


class UserCreateView(CreateView):
    form_class = CreateUserForm
    template_name = "registration/register.html"

    def dispatch(self, request, *args, **kwargs):
        """ Redirect to detail page if user is logged in. """
        user = request.user
        if user.is_authenticated:
            return redirect(reverse("user:detail", kwargs={"username": user.username}))
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """ Login user after account is created. """
        form.save()
        username = self.request.POST["username"]
        password = self.request.POST["password2"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        user = self.request.user
        messages.success(self.request, "Ditt konto har skapats!")
        return reverse("user:detail", kwargs={"username": user.username})


class UserDetailView(DetailView):
    template_name = "users/detail.html"

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        profiles = ["football_player"]
        user_profiles = []
        for profile in profiles:
            if hasattr(user, profile):
                user_profiles.append(getattr(user, profile))
        context['profiles'] = user_profiles
        context['form'] = PmMessageForm
        return context

    def get_object(self, queryset=None):
        """ Prevent duplicate queries when retrieving object in other methods. """
        if not hasattr(self, "object"):
            username = self.kwargs["username"]
            user = get_object_or_404(
                User.objects.select_related('city', 'football_player'),
                username=username
            )
            self.object = user
        return self.object


class UserLoginView(LoginView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        """ Redirect to detail page if user is already logged in. """
        user = request.user
        if user.is_authenticated:
            return redirect(reverse("user:detail", kwargs={"username": user.username}))
        else:
            return super().dispatch(request, *args, **kwargs)


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """ Used by LOGIN_REDIRECT_URL in settings/base.py """
    def get_redirect_url(self):
        user = self.request.user
        return reverse("user:detail", kwargs={"username": user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/update.html"
    form_class = UpdateUserForm

    def get_object(self, queryset=None):
        user = self.request.user
        return user
    
    def get_success_url(self):
        messages.success(self.request, "Inställningarna sparades!")
        return self.object.get_absolute_url()


class UserDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self, queryset=None):
        user = self.request.user
        return user
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse("index")


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_success_url(self):
        user = self.request.user
        messages.success(self.request, "Ditt lösenord har ändrats!")
        return reverse("user:detail", kwargs={"username": user.username})

