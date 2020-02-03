from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    View,
)
from .forms import TeamForm, TeamCreateForm
from .models import Team


'''
Next iteration:
- Go through each view make sure they do dispatch/get_object properly
- Go through each view make sure they meet standard..
- list view.. filter (seeking, not seeking, all)
- consequences of deleting a team when it comes to conversations (ad) etc..
'''


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~~   MIXINS   ~~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class TeamCheckMixin:
    '''
    Redirect to team:create page if client does not a team. Used by
    TeamUpdateView, TeamDeleteView, and UpdateTeamStatus. 
    '''
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']
        
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        obj = self.get_object()

        ''' If obj is None it means that user does not have the required team
        and should thus be redirected to the create page. '''

        if obj is None:
            return redirect(reverse("team:create", kwargs={"sport": sport}))
        else:
            return super().dispatch(request, *args, **kwargs)

        
class GetObjectMixin:
    ''' Used by TeamUpdateView, TeamDeleteView, and UpdateTeamStatus. '''
    def get_object(self, queryset=None):
        user = self.request.user
        sport = self.kwargs['sport']

        if not hasattr(self, 'object'):
            try:
                self.object = Team.objects.get(sport=sport, user=user)
            except Team.DoesNotExist:
                self.object = None
        return self.object


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~~   VIEWS   ~~~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class TeamDetailView(DetailView):
    template_name = "teams/detail.html"

    def get_object(self, queryset=None):
        sport = self.kwargs['sport']
        team_id = self.kwargs['team_id']
        slug = self.kwargs['slug']

        if not hasattr(self, "object"):
            obj = get_object_or_404(
                Team.objects.select_related('user', 'city'),
                sport=sport,
                team_id=team_id,
                slug=slug
            )
            self.object = obj
        
        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if obj.is_looking:
            context['status'] = "Ja"
        else:
            context['status'] = "Nej"
        return context


class TeamCreateView(CreateView):
    template_name = "teams/create.html"
    form_class = TeamCreateForm
    initial = { "founded": "2000" }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect to team:detail page if user already has a team. '''
        try:
            team = Team.objects.get(sport=sport, user=user)
        except Team.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)
        else:  
            return redirect(team.get_absolute_url())
        
    def get_form_kwargs(self):
        ''' Send sport kwarg to form, so that it can dynamically generate the
        right form. '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs

    def form_valid(self, form):
        ''' Assign the user object to the team. '''
        f = form.save(commit=False)
        f.user = self.request.user
        f.save()
        self.object = f
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Laget har skapats!")
        return self.object.get_absolute_url()
        
        
class TeamUpdateView(TeamCheckMixin, GetObjectMixin, UpdateView):
    template_name = "teams/update.html"
    form_class = TeamForm
    
    def get_form_kwargs(self):
        ''' Send sport kwarg to form, so that it can dynamically generate the
        right form. '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, "Laget har uppdaterats!")
        return self.object.get_absolute_url()


class TeamDeleteView(TeamCheckMixin, GetObjectMixin, DeleteView):
    template_name = "teams/delete_confirmation.html"
    
    def get_success_url(self):
        messages.success(self.request, "Laget har tagits bort!")
        user = self.request.user
        return user.get_absolute_url()


class UpdateTeamStatus(TeamCheckMixin, GetObjectMixin, View):

    def post(self, request, *args, **kwargs):
        ''' Toggle the is_looking attribute of the team object. '''
        obj = self.get_object()
        if obj.is_looking:
            obj.is_looking = False
        else:
            obj.is_looking = True
        obj.save()
        messages.success(request, "Status har uppdaterats!")
        return redirect(obj.get_absolute_url())
