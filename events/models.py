from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='events')

    class Meta:
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date', 'time']),
        ]

    def __str__(self):
        return f"{self.name} — {self.date} {self.time}"


class Participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    events = models.ManyToManyField(Event, related_name='participants', blank=True)

    class Meta:
        unique_together = ('email',)  

    def __str__(self):
        return f"{self.name} <{self.email}>"
