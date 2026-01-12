from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Note(models.Model):

    text = models.CharField(max_length=250)
    tagged = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{str(self.created_at.date())} | הערה עבור - {self.content_object}'
    
    class Meta:
        indexes = [
            models.Index(fields = ['content_type', 'object_id']),
        ]
        verbose_name = "הערה"
        verbose_name_plural = 'הערות'
        ordering = ['-created_at']


class Task(models.Model):

    URGENCIES = (
        ('low', 'נמוכה'),
        ('medium', 'בינונית'),
        ('high', 'גבוהה'),
        ('critical', 'קריטית')
    )

    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    urgency = models.CharField(max_length=30, choices=URGENCIES, default='low')
    is_completed = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields = ['content_type', 'object_id']),
        ]
        verbose_name = "משימה"
        verbose_name_plural = 'משימות'
        ordering = ['-created_at']
    
    @property
    def reported_timesheet(self):
        timesheets = sum( [x.hours for x in self.timesheets.all()])
        return timesheets

    @property
    def billed_timesheet(self):
        timesheets = sum( [x.hours for x in self.timesheets.all() if x.is_billed])
        return timesheets


class Service(models.Model):
    
    BUDGET_TYPES = (
        ('fix', 'קבוע'),
        ('hourly', 'שעתי'),
    )

    name = models.CharField(max_length=255)

    budget_type = models.CharField(max_length=255, choices=BUDGET_TYPES)
    is_subscription = models.BooleanField(default=False)
    default_qty = models.PositiveBigIntegerField()
    default_price = models.DecimalField(decimal_places=2, max_digits=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "שירות"
        verbose_name_plural = 'שירותים'
        ordering = ['-created_at']


class Timesheet(models.Model):

    date = models.DateField(default=timezone.now())
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    is_billed = models.BooleanField(default=False)

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timesheets')
    budget = models.ForeignKey('projects.ProjectBudget', on_delete=models.SET_NULL, null=True, related_name='timesheets')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.date} | {self.task.title} | {self.hours}'
    
    class Meta:
        verbose_name = 'דיווח שעות'
        verbose_name_plural = 'דיווחי שעות'
        ordering = ['-created_at']











