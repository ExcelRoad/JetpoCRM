from django.db import models
from projects.models import Project
from activities.models import Service

class Payment(models.Model):

    STATUSES = (
        ('draft', 'טיוטה'),
        ('billed', 'חוייב'),
        ('paid', 'שולם')
    )
    
    name = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    qty = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='payments')

    status = models.CharField(max_length=10, choices=STATUSES, default='draft')
    
    sumit_invoice_number = models.CharField(max_length=20, null=True, blank=True)
    sumit_recipt_number = models.CharField(max_length=20, null=True, blank=True)

    sumit_invoice_link = models.CharField(max_length=255, null=True, blank=True)
    sumit_recipt_link = models.CharField(max_length=255, null=True, blank=True)

    invoice_date = models.DateField(null=True, blank=True)
    recipt_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "תשלום"
        verbose_name_plural = 'תשלומים'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    @property
    def total_price(self):
        return self.qty * self.price

    @property
    def payment_number(self):
        number = 60000 + self.id
        return f'P-{number}'
    
    @property
    def vat_amount(self):
        return float(self.total_price) * 0.18
    
    @property
    def total_wvat_price(self):
        return float(self.total_price) + self.vat_amount