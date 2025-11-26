from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError

from .forms import SignUpForm, EventForm
from .models import Event, Category, RSVP
from .decorators import group_required, groups_required
from django.contrib.auth.decorators import login_required

def home(request):
    return redirect("event_list")

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created. Please check your email to activate your account.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. You can now log in.")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid.")
        return redirect("home")

def login_view(request):
    if request.user.is_authenticated:
        # Already logged in - redirect based on role
        return redirect_role_dashboard(request.user)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Account not activated. Check your email.")
                return redirect("login")
            login(request, user)
            return redirect_role_dashboard(user)
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "login.html", {})

def redirect_role_dashboard(user):
    if user.is_superuser or user.groups.filter(name="Admin").exists():
        return redirect("admin_dashboard")
    if user.groups.filter(name="Organizer").exists():
        return redirect("organizer_dashboard")
    # default Participant
    return redirect("participant_dashboard")

def logout_view(request):
    logout(request)
    return redirect("login")

def event_list(request):
    qs = Event.objects.all().order_by("-start_time")
    return render(request, "event_list.html", {"events": qs})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvped = False
    if request.user.is_authenticated:
        user_rsvped = RSVP.objects.filter(user=request.user, event=event).exists()
    return render(request, "event_detail.html", {"event": event, "user_rsvped": user_rsvped})

@groups_required("Organizer", "Admin")
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.organizer = request.user
            ev.save()
            form.save_m2m()
            messages.success(request, "Event created")
            return redirect("event_detail", pk=ev.pk)
    else:
        form = EventForm()
    return render(request, "event_form.html", {"form": form})

@groups_required("Organizer", "Admin")
def event_edit(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    # organizers can edit only their events unless admin
    if not request.user.groups.filter(name="Admin").exists() and ev.organizer != request.user:
        messages.error(request, "Not allowed")
        return redirect("event_list")
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=ev)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated")
            return redirect("event_detail", pk=ev.pk)
    else:
        form = EventForm(instance=ev)
    return render(request, "event_form.html", {"form": form, "event": ev})

@groups_required("Organizer", "Admin")
def event_delete(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    if not request.user.groups.filter(name="Admin").exists() and ev.organizer != request.user:
        messages.error(request, "Not allowed")
        return redirect("event_list")
    if request.method == "POST":
        ev.delete()
        messages.success(request, "Event deleted")
        return redirect("event_list")
    return render(request, "event_confirm_delete.html", {"event": ev})

@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    try:
        rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
        if not created:
            messages.info(request, "You have already RSVP'd to this event.")
        else:
            messages.success(request, "RSVP successful. Confirmation email sent.")
    except IntegrityError:
        messages.error(request, "Could not RSVP. Try again.")
    return redirect("event_detail", pk=pk)

@group_required("Admin")
def admin_dashboard(request):
    events = Event.objects.all().order_by("-created_at")
    users = User.objects.all()
    categories = Category.objects.all()
    return render(request, "admin_dashboard.html", {"events": events, "users": users, "categories": categories})

@groups_required("Organizer", "Admin")
def organizer_dashboard(request):
    # organizer sees only their events
    if request.user.groups.filter(name="Admin").exists():
        events = Event.objects.all()
    else:
        events = Event.objects.filter(organizer=request.user)
    categories = Category.objects.all()
    return render(request, "organizer_dashboard.html", {"events": events, "categories": categories})

@group_required("Participant")
def participant_dashboard(request):
    rsvps = request.user.rsvped_events.all().order_by("-start_time")
    return render(request, "participant_dashboard.html", {"rsvped_events": rsvps})