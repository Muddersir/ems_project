from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import RSVP, Event

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        # Ensure the Participant group exists and assign new users to Participant by default
        participant_group, _ = Group.objects.get_or_create(name="Participant")
        instance.groups.add(participant_group)
        # Build activation link
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        activation_path = reverse("activate", kwargs={"uidb64": uid, "token": token})
        activation_link = f"{getattr(settings,'SITE_URL','http://localhost:8000')}{activation_path}"
        subject = "Activate your account"
        message = f"Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n\n{activation_link}\n\nIf you didn't sign up, ignore this message."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)

@receiver(post_save, sender=RSVP)
def on_rsvp_created(sender, instance, created, **kwargs):
    if not created:
        return
    # Send confirmation email to the user who RSVPed
    user = instance.user
    event = instance.event
    subject = f"RSVP Confirmation for {event.title}"
    message = f"Hi {user.first_name or user.username},\n\nYou have successfully RSVP'd to {event.title}.\nEvent starts at: {event.start_time}.\n\nThank you."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    # Notify organizer about new RSVP
    organizer = event.organizer
    if organizer.email:
        subj2 = f"New RSVP for your event '{event.title}'"
        msg2 = f"Hi {organizer.first_name or organizer.username},\n\n{user.username} has RSVP'd to your event: {event.title}."
        send_mail(subj2, msg2, settings.DEFAULT_FROM_EMAIL, [organizer.email], fail_silently=True)