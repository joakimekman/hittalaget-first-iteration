from django.urls import path
from . import views

app_name = "conversation"

# kolla så att URL's works... tydligen så spelar ordning på path converters också.. alphabetical order,
# i.e. <int> kommer före <str> ?? <--- add

urlpatterns = [
    # AD
    path('<int:conversation_id>/', views.AdDetailView.as_view(), name="ad_detail"),
    path('<int:conversation_id>/ta-bort/', views.AdDeleteView.as_view(), name="ad_delete"),
    path('<int:conversation_id>/posta-meddelande/', views.AdCreateMessage.as_view(), name="ad_create_message"),
    path('<int:ad_id>/kontakta/', views.AdCreateConversation.as_view(), name="ad_create_conversation"),
    
    # PM
    path('<str:username>/', views.PmDetailView.as_view(), name="pm_detail"),
    path('<str:username>/ta-bort/', views.PmDeleteView.as_view(), name="pm_delete"),
    path('<str:username>/posta-meddelande/', views.PmCreateMessage.as_view(), name="pm_create_message"),

    path('', views.ConversationListView.as_view(), name="list"),
]

'''
hittalaget.se/konversationer/ --> ListView (should be able to filter pm from ad?)
'''



