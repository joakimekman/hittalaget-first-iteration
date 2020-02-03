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
    UpdateView,
    ListView,
)
from .models import Ad
from .forms import AdForm
from hittalaget.teams.models import Team
from hittalaget.conversations.forms import AdMessageForm


'''
Next iteration:
- future feature: matching system..
- consequences of deleting a ad when it comes to conversations (ad) etc..
'''


class AdDetailView(DetailView):
    template_name = "ads/detail.html"

    def get_object(self, queryset=None):
        ad_id = self.kwargs['ad_id']
        
        if not hasattr(self, 'object'):
            self.object = get_object_or_404(Ad.objects.select_related('team__user'), ad_id=ad_id) # should I do this in team too? it is after all a unique identifier
        
        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdMessageForm
        return context


class AdListView(ListView):
    template_name = "ads/list.html"

    def get_queryset(self):
        sport = self.kwargs['sport']
        queryset = Ad.objects.filter(sport=sport)
        return queryset


class AdCreateView(CreateView):
    template_name = "ads/create.html"
    form_class = AdForm

    def dispatch(self, request, *args, **kwargs):
        '''
        Only authorized users with a team can create an ad. Redirect..
        '''
        user = request.user
        sport = kwargs['sport']

        # redirect client to login page if unauthorized
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' is there any way you can do this through the user object? or will it lead to an additional query either way? '''
        if Team.objects.filter(user=user, sport=sport).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse('user:detail', kwargs={"username": user.username}))

    def get_form_kwargs(self):
        '''
        Pass sport to the form so that it can generate the right
        form choices.
        '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs

    def form_valid(self, form):
        '''
        Assign team, and sport to ad, and change status of team..
        '''
        f = form.save(commit=False)
        sport = self.kwargs['sport']
        user = self.request.user
        team = Team.objects.get(user=user, sport=sport)
        f.team = team
        f.sport = sport
        f.save()
        self.object = f

        if not team.is_looking:
            team.is_looking = True
            team.save()
        
        return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        '''
        Redirect to ad detail page.
        '''
        messages.success(self.request, 'Annonsen skapades utan problem!')
        return self.object.get_absolute_url()


class AdDeleteView(DeleteView):
    template_name = "ads/delete_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        obj = self.get_object()

        if obj.team.user == user:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_object(self, queryset=None):
        ad_id = self.kwargs['ad_id']

        if not hasattr(self, 'object'):
            self.object = get_object_or_404(Ad, ad_id=ad_id)
        
        return self.object

    def get_success_url(self):
        '''
        Perhaps you would want to redirect to some sort of ads.. or team profile..???
        '''
        messages.success(self.request, 'Annonsen togs bort utan problem!')
        return reverse('user:detail', kwargs={"username": self.request.user.username})
