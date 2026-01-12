from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from activities.models import Note, Task, Service

class Quote(models.Model):

    """
    This is the quote model that store all the quotes data. quotes can be related to leads or customers.
    When quote is approved, multiple projects are created (one per service line item) and payments
    related to each project will be created.
    """

    STATUSES = (
        ('draft', 'טיוטה'),
        ('lost', 'אבודה'),
        ('won', 'מאושרת'),
        ('sent', 'נשלחה'),
    )

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUSES, default='draft')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    notes = GenericRelation(Note, related_query_name='notes')
    tasks = GenericRelation(Task, related_query_name='tasks')

    folder_id = models.CharField(max_length=255, null=True, blank=True)
    folder_link = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields = ['content_type', 'object_id']),
        ]
        verbose_name = "הצעת מחיר"
        verbose_name_plural = 'הצעות מחיר'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_price(self):
        """Calculate total from sum of all service line items"""
        tAmount = 0
        for s in self.quote_services.all():
            tAmount = tAmount + s.total_price
        return tAmount


    @property
    def related_to(self):
        return f'{self.content_object} ({self.content_type.name})'

    @property
    def vat_amount(self):
        return float(self.total_price) * 0.18

    @property
    def total_wvat_price(self):
        return float(self.total_price) + self.vat_amount

    @property
    def quote_number(self):
        number = 10000 + self.id
        return f'Q-{number}'


class Quote_Service(models.Model):
    """
    Service line items in a quote. Each row represents a service with quantity and price.
    Multiple projects will be created from these when quote is confirmed.
    """

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='quote_services')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    qty = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "שירות הצעת מחיר"
        verbose_name_plural = 'שירותי הצעת מחיר'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.name} | {self.quote.quote_number}'

    @property
    def total_price(self):
        return self.qty * self.price


class Quote_Payment(models.Model):
    """
    Payments divide the quote total into installments.
    Each payment is linked to a specific service line item.
    """

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='quote_payments')
    quote_service = models.ForeignKey(Quote_Service, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    percent = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "תשלום הצעת מחיר"
        verbose_name_plural = 'תשלומי הצעת מחיר'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.name} | {self.quote.quote_number}'





