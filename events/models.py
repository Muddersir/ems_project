from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def event_image_default():
    # relative path in MEDIA_ROOT
    return "default_event.jpg"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="events/", default=event_image_default)

    attendees = models.ManyToManyField(User, through="RSVP", related_name="rsvped_events", blank=True)

    def __str__(self):
        return self.title

class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    # response could be 'yes', 'no', 'maybe' - for simplicity store 'yes' only for RSVP
    response = models.CharField(max_length=20, default="yes")

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.response})"