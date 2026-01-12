from django.db import models
from activities.models import Note
from quotes.models import Quote
from django.contrib.contenttypes.fields import GenericRelation


class Lead(models.Model):
    """
    This is the lead model that get all the lead information. the leads are created from verious lead sources and
    created into the CRM from API endpoints.
    In the lead the user will manage quotes, notes and tasks.
    """
    LEAD_STATUSES = (
        ('new', 'חדש'),
        ('follow', 'במעקב'),
        ('quote', 'הצעת מחיר'),
        ('won', 'ליד מומר'),
        ('lost', 'אבוד'),
        ('trash', 'זבל'),
    )
    
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True)
    company_name = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=50, choices=LEAD_STATUSES, default='new')
    role = models.CharField(max_length=250, blank=True, null=True)
    lead_source = models.ForeignKey('LeadSource', on_delete=models.SET_NULL, null=True, blank=True)

    notes = GenericRelation(Note, related_query_name='notes')
    quotes = GenericRelation(Quote, related_query_name='quotes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ליד'
        verbose_name_plural = 'לידים'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def phone_number(self):
        n = ''.join(filter(str.isdigit, self.phone))
        return f'{n[:3]}-{n[3:6]}-{n[6:]}'




class LeadSource(models.Model):
    """
    Lead sources that leads are generating from.
    There to analyze leads to improve lead generation.
    """
    name = models.CharField(max_length=250, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'מקור ליד'
        verbose_name_plural = 'מקורות ליד'
    
    def __str__(self):
        return self.name