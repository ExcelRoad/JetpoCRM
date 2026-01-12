from django.db import models
from activities.models import Note
from quotes.models import Quote
from django.contrib.contenttypes.fields import GenericRelation
from customers.models import Customer


class Contact(models.Model):

    TYPES = (
        ('normal', 'רגיל'),
        ('accounting', 'חשבונות'),
    )

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True)
    role = models.CharField(max_length=250, blank=True, null=True)
    contact_type = models.CharField(max_length=30, choices=TYPES, default='normaml', null=True)

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='contacts')

    notes = GenericRelation(Note, related_query_name='notes')
    quotes = GenericRelation(Quote, related_query_name='quotes')

    is_main = models.BooleanField(default=False)
    is_alerts = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'איש קשר'
        verbose_name_plural = 'אנשי קשר'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def phone_number(self):
        n = ''.join(filter(str.isdigit, self.phone))
        return f'{n[:3]}-{n[3:6]}-{n[6:]}'