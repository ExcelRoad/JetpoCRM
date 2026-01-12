from django.db import models
from leads.models import LeadSource
from django.contrib.contenttypes.fields import GenericRelation
from activities.models import Note
from quotes.models import Quote

class Customer(models.Model):

    name = models.CharField(max_length=255)
    legal_id = models.CharField(max_length=30)
    logo = models.ImageField(upload_to='customer_logos/', null=True, blank=True)
    sumit_id = models.CharField(max_length=30, null=True, blank=True)
    folder_id = models.CharField(max_length=100, null=True, blank=True)
    folder_link = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    lead_source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True)

    notes = GenericRelation(Note, related_query_name='notes')
    quotes = GenericRelation(Quote, related_query_name='quotes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "לקוח"
        verbose_name_plural = "לקוחות"

    @property
    def total_income(self):
        return 100
    
    @property
    def open_quotes(self):
        quotes = self.quotes.all().filter(status__in=['draft', 'sent'])
        count = 0
        value = 0
        for q in quotes:
            count += 1
            value += q.total_price
        
        open_quotes_map = {
            'value': value,
            'count': count,
        }
        return open_quotes_map
    
    @property
    def open_projects(self):
        projects = self.projects.all().filter(status = 'open')
        count = 0
        value = 0
        for p in projects:
            count += 1
            value += p.budget.get('amount')
        open_project_map = {
            'value': value,
            'count': count,
        }
        return open_project_map
