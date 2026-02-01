from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
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
        return f'{self.date} | {self.task.title} | {self.hours} שעות'
    
    class Meta:
        verbose_name = 'דיווח שעות'
        verbose_name_plural = 'דיווחי שעות'
        ordering = ['-created_at']


class Meeting(models.Model):

    STATUSES = (
        ('pending', 'ממתין'),
        ('completed', 'הושלם'),
        ('canceled', 'בוטל'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(default=timezone.now())
    start_time = models.TimeField()
    duration = models.DecimalField(max_digits=2, decimal_places=0)
    is_online = models.BooleanField(default=False)
    online_url = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=100, choices=STATUSES, default='pending')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        # set the customer if its not a lead
        if not self.customer:
            if self.content_type.model != 'lead':
                if self.content_object.customer:
                    self.customer = self.content_object.customer
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "פגישה"
        verbose_name_plural = 'פגישות'
        ordering = ['-created_at']
    
    @property
    def start_datetime(self):
        return datetime.combine(self.date, self.start_time)
    
    @property
    def end_datetime(self):
        endTime = datetime.combine(self.date, self.start_time) + timedelta(minutes=int(self.duration))
        return endTime












