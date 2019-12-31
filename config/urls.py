from django.conf import settings
from django.contrib.auth.views import (
  PasswordResetView,
  PasswordResetDoneView,
  PasswordResetConfirmView,
  PasswordResetCompleteView,
)
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path('contact/', TemplateView.as_view(template_name="pages/contact.html"), name="contact"),

    path('reset-password/', PasswordResetView.as_view(), name="password_reset"),
    path('reset-password/email-sent/', PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset-password/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('', TemplateView.as_view(template_name="pages/index.html"), name="index"),
    path('', include('hittalaget.users.urls', namespace="user")),
]

if settings.DEBUG:
  import debug_toolbar

  urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
  ]

  