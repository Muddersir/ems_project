from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('event/add/', views.EventCreateView.as_view(), name='add'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('event/<int:pk>/register/', views.ParticipantRegisterView.as_view(), name='register'),
]

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event URLs
    path('', views.EventListView.as_view(), name='list'),
    path('event/add/', views.EventCreateView.as_view(), name='add'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete'),
    path('event/<int:pk>/register/', views.ParticipantRegisterView.as_view(), name='register'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Participant URLs
    path('participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/add/', views.ParticipantCreateView.as_view(), name='participant_add'),
    path('participants/<int:pk>/edit/', views.ParticipantUpdateView.as_view(), name='participant_edit'),
    path('participants/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
]

# events/urls.py
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('event/add/', views.EventCreateView.as_view(), name='add'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete'),
    path('event/<int:pk>/register/', views.ParticipantRegisterView.as_view(), name='register'),

    # Participants
    path('participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/add/', views.ParticipantCreateView.as_view(), name='participant_add'),
    path('participants/<int:pk>/edit/', views.ParticipantUpdateView.as_view(), name='participant_edit'),
    path('participants/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Organizer dashboard
    path('dashboard/', views.OrganizerDashboardView.as_view(), name='dashboard'),
    path('dashboard/events-json/', views.dashboard_events_json, name='dashboard_events_json'),
    path('dashboard/stats-json/', views.dashboard_stats_json, name='dashboard_stats_json'),
]
