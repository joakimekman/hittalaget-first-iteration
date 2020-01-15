from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "player"

urlpatterns = [
  path("<str:sport>/ny/", views.PlayerCreateView.as_view(), name="create"),
  path("<str:sport>/uppdatera/", views.PlayerUpdateView.as_view(), name="update"),
  path("<str:sport>/ta-bort/", views.PlayerDeleteView.as_view(), name="delete"),
  path("<str:sport>/uppdatera-status/", views.UpdatePlayerStatus.as_view(), name="update_status"),
  path("<str:sport>/lagg-till-historik/", views.CreatePlayerHistory.as_view(), name="create_history"),
  path("<str:sport>/historik/<int:id>/uppdatera/", views.UpdatePlayerHistory.as_view(), name="update_history"),
  path("<str:sport>/historik/<int:id>/ta-bort/", views.DeletePlayerHistory.as_view(), name="delete_history"),
  path("<str:sport>/<str:username>/", views.PlayerDetailView.as_view(), name="detail"),
]

