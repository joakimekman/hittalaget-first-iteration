from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    RedirectView,
    UpdateView,
    View,
)
from .forms import FootballPlayerForm, FootballHistoryForm
from .models import FootballPlayer, FootballHistory


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~~   MIXINS   ~~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class GetFormClassMixin:
    """
    Return the right form for the right sport. Used by
    PlayerCreateView, and PlayerUpdateView.
    """
    def get_form_class(self):
        sport = self.kwargs['sport']
        forms = {
            "fotboll": FootballPlayerForm,
        }
        try:
            form = forms[sport]
        except KeyError:
            raise Http404()
        return form


class GetObjectMixin:
    """
    Return the right player profile for the logged-in user.
    Used by PlayerUpdateView, PlayerDeleteView and UpdatePlayerStatus.
    """
    def get_object(self, queryset=None):
        user = self.request.user
        sport = self.kwargs['sport']
        
        profiles = {
            "fotboll": "football_player",
        }

        '''
        The dispatch() method of classes that uses this mixin will check
        if user has profile and for KeyError, so we don't have to repeat
        that process here. We simply have to get and return the object.
        '''
            
        if not hasattr(self, "object") or self.object is None:
            profile = getattr(user, profiles[sport])
            self.object = profile
        return self.object


class GetSuccessUrlMixin:
    """
    Return the url for the player detail page. Used by
    PlayerCreateView, and PlayerUpdateView.
    """
    def get_success_url(self):
        return self.object.get_absolute_url()
        

class ProfileCheckMixin:
    """
    Check if user has profile, and for KeyError. If user does not 
    have profile, user will be redirected to create one. Used by 
    PlayerUpdateView, PlayerDeleteView, UpdatePlayerStatus, UpdatePlayerHistory,
    and DeletePlayerHistory.

    Also, client will be redirected to the login page if not 
    authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        profiles = {
            "fotboll": "football_player",
        }
    
        # redirect client to login page if unauthorized
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        try:
            if hasattr(user, profiles[sport]):
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect(reverse("player:create", kwargs={"sport": sport}))
        except KeyError:
            raise Http404()


#   ---------------------------------------   #
#   ~~~~~~~~~~~   PLAYER VIEWS   ~~~~~~~~~~   #            
#   ---------------------------------------   #


class PlayerDetailView(DetailView):
    template_name = "players/detail.html"

    def get_object(self, queryset=None):
        sport = self.kwargs['sport']
        username = self.kwargs['username']

        models = {
            "fotboll": FootballPlayer,
        }
        
        try:
            if not hasattr(self, "object"):
                self.object = get_object_or_404(
                    models[sport].objects.select_related('user'),
                    username=username
                )
        except KeyError:
            raise Http404()
        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        if profile.is_available:
            context['status'] = "söker klubb"
        else:
            context['status'] = "upptagen"
        return context


class PlayerCreateView(GetFormClassMixin, GetSuccessUrlMixin, CreateView):
    template_name = "players/create.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect user to its player detail page if user already
        has a player profile for that sport.
        """
        user = request.user
        sport = kwargs['sport']

        # redirect client to login page if unauthorized
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        profiles = {
            "fotboll": "football_player",
        }

        try:
            if hasattr(user, profiles[sport]):
                profile = getattr(user, profiles[sport])
                return redirect(profile.get_absolute_url())
            else:
                return super().dispatch(request, *args, **kwargs)
        except KeyError:
            raise Http404()


    def form_valid(self, form):
        f = form.save(commit=False)
        user = self.request.user
        f.user = user
        f.username = user.username
        f.save()
        self.object = f
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Spelarprofilen skapades utan problem!")
        return super().get_success_url()


class PlayerUpdateView(ProfileCheckMixin, GetFormClassMixin, GetObjectMixin, GetSuccessUrlMixin, UpdateView):
    template_name = "players/update.html"

    def get_success_url(self):
        messages.success(self.request, "Profilen har uppdaterats!")
        return super().get_success_url()


class PlayerDeleteView(ProfileCheckMixin, GetObjectMixin, DeleteView):
    template_name = "players/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Profilen har raderats!")
        user = self.request.user
        return user.get_absolute_url()
 

class UpdatePlayerStatus(ProfileCheckMixin, GetObjectMixin, View):
    """
    Toggles the available property of a player profile.
    """

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        
        if profile.is_available:
            profile.is_available = False
        else:
            profile.is_available = True
        profile.save()

        messages.success(request, "Din tillgänglighet har uppdaterats!")
        return redirect(profile.get_absolute_url())        


#   ---------------------------------------   #
#   ~~~~~~~~~~   HISTORY MIXINS   ~~~~~~~~~   #            
#   ---------------------------------------   #


class PermissionMixin:
    """
    Used by UpdatePlayerHistory and DeletePlayerHistory view to
    make sure only the owner can modify and delete its history entry.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        '''
        The UpdatePlayerHistory and DeletePlayerHistory view should
        have access to the get_object() method through the 
        GetHistoryObjectMixin.
        '''

        # redirect client to login page if unauthorized
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        history_entry = self.get_object()

        if history_entry.player.username == user.username:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()


class GetHistoryFormClassMixin:
    def get_form_class(self):
        sport = self.kwargs['sport']

        forms = {
            "fotboll": FootballHistoryForm,
        }

        try:
            form = forms[sport]
        except KeyError:
            raise Http404()
        return form


class GetHistoryObjectMixin:
    def get_object(self, queryset=None):
        sport = self.kwargs['sport']
        entry_id = self.kwargs['id']
        
        models = {
            "fotboll": FootballHistory,
        }

        try:
            if not hasattr(self, "object"):
                self.object = get_object_or_404(models[sport], id=entry_id)
        except KeyError:
            raise Http404()
        return self.object


class GetHistorySuccessUrlMixin:
    def get_success_url(self):
        sport = self.kwargs['sport']
        user = self.request.user
        return reverse("player:detail", kwargs={"sport": sport, "username": user.username})


#   ---------------------------------------   #
#   ~~~~~~~~~~   HISTORY VIEWS   ~~~~~~~~~~   #            
#   ---------------------------------------   #


class CreatePlayerHistory(ProfileCheckMixin, GetObjectMixin, GetHistoryFormClassMixin, GetHistorySuccessUrlMixin, CreateView):
    template_name = "players/create_history.html"
    initial = {
        "start_year": "2000",
        "end_year": "2000",
    }

    def form_valid(self, form):
        f = form.save(commit=False)
        f.player = self.get_object()
        f.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, "Historiken har skapats!")
        return super().get_success_url()


class UpdatePlayerHistory(PermissionMixin, ProfileCheckMixin, GetHistoryFormClassMixin, GetHistoryObjectMixin, GetHistorySuccessUrlMixin, UpdateView):
    template_name = "players/update_history.html"

    def get_success_url(self):
        messages.success(self.request, "Historiken har uppdaterats!")
        return super().get_success_url()


class DeletePlayerHistory(PermissionMixin, ProfileCheckMixin, GetHistoryObjectMixin, GetHistorySuccessUrlMixin, DeleteView):
    template_name = "players/delete_history_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Historiken har raderats!")
        return super().get_success_url()

