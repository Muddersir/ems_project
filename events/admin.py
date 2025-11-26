from django.contrib import admin
from .models import Event, Category, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "start_time", "end_time")
    search_fields = ("title", "description", "organizer__username")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "response", "timestamp")
    search_fields = ("user__username", "event__title")