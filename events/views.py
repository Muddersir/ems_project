from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date

from .models import Event, Category, Participant
from .forms import EventForm, ParticipantForm, CategoryForm
# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.shortcuts import get_object_or_404, redirect
from .models import Event, Category, Participant
from .forms import EventForm, ParticipantForm
from django.db.models import Prefetch

# List of events: use select_related for category and prefetch participants
class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'events/event_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = (Event.objects
              .select_related('category')                      # single join for category
              .prefetch_related('participants')                # prefetch participants
              .annotate(num_participants=Count('participants'))# annotate participant count
              .order_by('date', 'time'))

        # --- Search: name or location (case-insensitive)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))

        # --- Category filter (by id)
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category_id=cat)

        # --- Date range
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        if start and end:
            qs = qs.filter(date__range=[start, end])

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['total_participants'] = Participant.objects.count()
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return (Event.objects
                .select_related('category')
                .prefetch_related('participants'))


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:list')


# Participant registration for a single event using a FormView
class ParticipantRegisterView(FormView):
    form_class = ParticipantForm
    template_name = 'events/participant_register.html'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # See if participant with that email already exists; reuse or create
        email = form.cleaned_data['email']
        participant, created = Participant.objects.get_or_create(email=email, defaults={
            'name': form.cleaned_data['name']
        })
        # If existing, optionally update name if different
        if not created and participant.name != form.cleaned_data['name']:
            participant.name = form.cleaned_data['name']
            participant.save(update_fields=['name'])

        # Add the event (avoids duplicate via M2M if already exists)
        participant.events.add(self.event)
        return redirect('events:detail', pk=self.event.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['event'] = self.event
        return ctx


from django.views.generic import UpdateView, DeleteView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime

# -----------------------------------
# Event CRUD
# -----------------------------------

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:list')


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:list')


# -----------------------------------
# Category CRUD
# -----------------------------------

from .models import Category
from django import forms

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('events:category_list')


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('events:category_list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    success_url = reverse_lazy('events:category_list')


# -----------------------------------
# Participant CRUD
# -----------------------------------

class ParticipantListView(ListView):
    model = Participant
    template_name = 'events/participant_list.html'
    context_object_name = 'participants'


class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    success_url = reverse_lazy('events:participant_list')


class ParticipantUpdateView(UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    success_url = reverse_lazy('events:participant_list')


class ParticipantDeleteView(DeleteView):
    model = Participant
    template_name = 'events/participant_confirm_delete.html'
    success_url = reverse_lazy('events:participant_list')

class OrganizerDashboardView(TemplateView):
    template_name = 'events/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()

        # Basic stats
        total_participants = Participant.objects.count()
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(date__gte=today).count()
        past_events = Event.objects.filter(date__lt=today).count()

        # Today's events: optimized
        todays_events = (Event.objects
                         .filter(date=today)
                         .select_related('category')
                         .prefetch_related('participants')
                         .annotate(num_participants=Count('participants'))
                         .order_by('time'))

        ctx.update({
            'total_participants': total_participants,
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'todays_events': todays_events,
            'today': today,
        })
        return ctx
   
def dashboard_events_json(request):
      f = request.GET.get('filter', 'all')
      today = date.today()
      qs = Event.objects.select_related('category').prefetch_related('participants').annotate(num_participants=Count('participants'))

      if f == 'upcoming':
        qs = qs.filter(date__gte=today).order_by('date', 'time')
      elif f == 'past':
        qs = qs.filter(date__lt=today).order_by('-date', 'time')
      elif f == 'today':
        qs = qs.filter(date=today).order_by('time')
      else:
        # 'all' or unspecified
        qs = qs.order_by('date', 'time')

    # Build JSON-serializable list
      events = [{
        'id': e.id,
        'name': e.name,
        'date': e.date.isoformat(),
        'time': e.time.strftime('%H:%M'),
        'location': e.location,
        'category': e.category.name if e.category else None,
        'num_participants': e.num_participants,
    } for e in qs[:100]]  # limit to first 100 for safety

      return JsonResponse({'events': events})

def dashboard_stats_json(request):
    today = date.today()
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    return JsonResponse({
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })