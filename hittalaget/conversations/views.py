from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    View,
    ListView,
)
from .models import PmConversation, AdConversation, AdMessage
from .forms import PmMessageForm, AdMessageForm
from hittalaget.ads.models import Ad
from hittalaget.players.models import FootballPlayer

User = get_user_model()

'''
Next iteration:
- change urls names... from ad_detail to detail_ad..
- special formatting for the message when someone leaves AdConversation..
- add ad to the conversation for reference, and possibly the player profile for
easy check..
# improve on next iteraton:
# ----------------------------------------------------
# - add timestamp to see when a message was sent..
# - add index for AdConversation for faster lookups
'''


class ConversationListView(ListView):
    template_name = "conversations/list.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        q = PmConversation.objects.filter(users=user)
        return q
    
    # possible best practice: Add two querysets with ListView
    def get_context_data(self, **kwargs):
        ''' Add second queryset. '''
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['ad_conversations'] = AdConversation.objects.filter(users=user)
        return context 


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~   PM VIEWS   ~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class PmDetailView(DetailView):
    template_name = "conversations/detail_pm.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']
        
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to access conversation with self. '''
        if username == user.username:
            return redirect("conversation:list")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PmMessageForm
        return context

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = self.request.user

        if not hasattr(self, 'object'):
            try:
                ''' Get conversation if one exist between users. '''
                obj = PmConversation.objects.get(users=user, users_arr__icontains=username)
                self.object = obj
            except PmConversation.DoesNotExist:
                raise Http404()
        
        return self.object


class PmDeleteView(DeleteView):
    template_name = "conversations/delete_pm.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to delete conversation with self. '''
        if username == user.username:
            return redirect("conversation:list")
        
        ''' Proceed if conversation exist, otherwise redirect. '''
        if self.get_object() is not None:
            return super().dispatch(request, *args, **kwargs) ######
        else:
            return redirect(reverse("conversation:list"))

    def get_object(self, queryset=None):
        user = self.request.user
        username = self.kwargs['username']

        if not hasattr(self, 'object'):
            try:
                obj = PmConversation.objects.get(users=user, users_arr__icontains=username)
                self.object = obj
            except PmConversation.DoesNotExist:
                self.object = None

        return self.object
        
    def delete(self, request, *args, **kwargs):
        ''' Remove user from conversation. We know at this stage
        that the conversation exist. '''
        obj = self.get_object()
        user = request.user
        obj.users.remove(user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        ''' return to conversation:list '''
        messages.success(self.request, "Konversationen är borttagen!")
        return reverse("conversation:list")


class PmCreateMessage(View):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if users try to message self. ''' 
        if username == user.username:
            return redirect(reverse("conversation:list"))

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = kwargs['username']
        sender = request.user
        receiver = get_object_or_404(User, username=username)

        try:
            ''' Get conversation if one exist between users. '''
            conversation = PmConversation.objects.get(users=sender, users_arr__icontains=username)
        except PmConversation.DoesNotExist:
            ''' Create conversation if one does not exist between users. '''
            conversation = PmConversation()
            conversation.users_arr = [username, sender.username]
            conversation.save()

        ''' Re-add users in case someone left the conversation. '''
        conversation.users.add(sender, receiver) # will add if not in there..

        form = PmMessageForm(request.POST)

        if form.is_valid():
            ''' Add conversation, and author to the message. '''
            message = form.save(commit=False)
            message.conversation = conversation
            message.author = sender
            message.save()

        return redirect(reverse('conversation:pm_detail', kwargs={"username": username}))


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~   AD VIEWS   ~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class AdDetailView(DetailView):
    template_name = "conversations/detail_ad.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
    
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, 403 if user is not part
        of the conversation, otherwise proceed as normal. '''
        if user not in self.get_object().users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdMessageForm
        return context

    def get_object(self, queryset=None):
        conversation_id = self.kwargs['conversation_id']

        if not hasattr(self, 'object'):
            ''' Get conversation if it exist, oterwise raise a 404. '''
            ''' select related => users (used in dispatch) '''
            obj = get_object_or_404(AdConversation, conversation_id=conversation_id)
            self.object = obj

        return self.object


class AdDeleteView(DeleteView):
    template_name = "conversations/delete_ad.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, 403 if user is not part of
        conversation, otherwise proceed as normal. '''
        if user not in self.get_object().users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        conversation_id = self.kwargs['conversation_id']

        if not hasattr(self, 'object'):
            ''' Get conversation if it exist, oterwise raise a 404. '''
            ''' select related => users (used in dispatch, and delete..) '''
            obj = get_object_or_404(AdConversation, conversation_id=conversation_id)
            self.object = obj

        return self.object

    def delete(self, request, *args, **kwargs):
        conversation = self.get_object()
        user = request.user

        if len(conversation.users.all()) < 2:
            ''' Delete the conversation if there is only one user left. '''
            conversation.delete()
        else:
            ''' Remove the user from the conversation, and set is_active to False. '''
            conversation.users.remove(user)
            conversation.is_active = False
            conversation.save()
            ''' Alert the remaining user in the conversation that the user has left. '''
            message = AdMessage()
            message.author = user
            message.content = "{} lämnade konversationen.".format(user)
            message.conversation = conversation
            message.save()
        
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Konversationen är borttagen!")
        return reverse('conversation:list')


class AdCreateConversation(View):
    ''' Handles messages sent from the ad detail page. Conversation will be
    created if one does not exist, otherwise the message sent will be added
    to the existing conversation. '''

    def dispatch(self, request, *args, **kwargs):
        user = request.user
    
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to contact its own ad. Raise 404 if ad does not exist. '''
        ad = self.get_ad()
        if ad.team.user == user:
            return redirect(ad.get_absoulte_url())

        ''' Redirect if user does not have player profile. '''
        if not FootballPlayer.objects.filter(user=user, sport=ad.sport).exists():
            # want to add message.. but not good idea to put message in dispatch..
            return redirect(ad.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def get_ad(self):
        ''' Custom get_object method to get the ad. '''
        ad_id = self.kwargs['ad_id']
        
        if not hasattr(self, 'ad'):
            ad = get_object_or_404(Ad, ad_id=ad_id) # select_related('team')
            self.ad = ad

        return self.ad
        
    def post(self, request, *args, **kwargs):
        user = request.user
        ad = self.get_ad()

        ''' Get conversation if one exist, otherwise create a new one. '''
        try:
            conversation = AdConversation.objects.get(users=user, ad=ad, is_active=True) 
        except AdConversation.DoesNotExist:
            conversation = AdConversation()
            conversation.ad = ad
            conversation.users_arr = [user.username, ad.team.user.username]
            conversation.save()

        ''' Assign conversation, and author to the message, and then create it. '''
        form = AdMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.author = user
            message.save()
            # add users
            conversation.users.add(user, ad.team.user)

        return redirect(conversation.get_absolute_url())


class AdCreateMessage(View):
    ''' Messages sent from the conversation detail page. '''
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, and a 403 if user
        is not part of the conversation. '''
        conversation = self.get_conversation()

        if user not in conversation.users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)
    
    def get_conversation(self):
        ''' Custom get_object method to get the conversation. '''
        conversation_id = self.kwargs['conversation_id']

        if not hasattr(self, 'conversation'):
            self.conversation = get_object_or_404(AdConversation, conversation_id=conversation_id)
        
        return self.conversation

    def post(self, request, *args, **kwargs):
        user = request.user
        conversation = self.get_conversation()

        ''' Create message IF the conversation is_active. Else, return an
        error message. '''
        if conversation.is_active:
            form = AdMessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.author = user
                message.conversation = conversation
                message.save()
        else:
            messages.error(request, "Denna konversation är stängd.")
            
        return redirect(conversation.get_absolute_url())



'''
You shouldn't have to worry about KeyError, 404's, in any other method than dispatch.
'''


'''
Another possible best practice:Think about the order of 302, 403, 404, etc
in the dispatch.. if you want 302 to login page before 404, do not call get_object
before it.

All redirects upon request, should be handled in dispatch method, so it catches both
GET and POST requests.
'''

''' probably better to be more specific... and not have a CreateMessage that
create message and conversation... (PM)... instead, keep that logic in it's own
class... for easier manipulation...'''

# potentiell best practice, if you need to access obj in dispatch, etc, and you
# are using View, create your own custom "get_<object>" method to pull the method from.

'''
Type up in best practices:
- Better with one universal URL, instead of having two different resources for one URL paramter, e.g.
<str:name> to represent team, and a player... kinda hard to work with..
- ^ do not allow two different resources for one URL param.. it will lead to complex, and additional queries.
Instead, use two URL params, one for each resource, or skip them altogether, and have a universal URL.
'''

'''
Get it up and working, then think about better names and possibly a better way to
implement this..
'''

'''
Research to next iteration:
- how to query queryset with params..
- best way to do messages.. look at other sites and copy..
- create instant messages, ajax? 
- create notifications?

- how to create conversation like twitch...or message like fiverrr..
'''


'''
change URL's, pm_detail => detail_pm

- encryption.. end-to-end.. etc... encryption algo.. etc..
'''