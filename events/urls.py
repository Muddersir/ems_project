from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("events/<int:pk>/rsvp/", views.rsvp_event, name="rsvp_event"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/participant/", views.participant_dashboard, name="participant_dashboard"),
]