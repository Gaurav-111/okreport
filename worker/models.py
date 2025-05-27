from django.db import models
from django.utils import timezone

WORKER_TYPE_CHOICES = (
    ('helper', 'Helper'),
    ('proficient', 'Proficient'),
)

class Worker(models.Model):
    name = models.CharField(max_length=100)
    worker_type = models.CharField(max_length=20, choices=WORKER_TYPE_CHOICES)
    daily_salary = models.IntegerField()
    date_of_joining = models.DateField(default=timezone.now)

    def present_days(self):
        return self.attendance_set.count()

    def total_salary(self):
        return self.present_days() * self.daily_salary

    def __str__(self):
        return self.name

class Attendance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('worker', 'date')  # Prevent double-marking for same day

    def __str__(self):
        return f"{self.worker.name} - {self.date}"
    




class ActivityLog(models.Model):
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description

