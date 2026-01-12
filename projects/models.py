from django.db import models
from customers.models import Customer
from django.contrib.contenttypes.fields import GenericRelation
from activities.models import Note, Task, Service

class Project(models.Model):

    STATUSES = (
        ('open', 'פתוח'),
        ('completed', 'הושלם'),
        ('canceled', 'בוטל'),
        ('onHold', 'ממתין'),
    )

    name = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=STATUSES, default='open')

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    notes = GenericRelation(Note, related_query_name='notes')
    tasks = GenericRelation(Task, related_query_name='tasks')

    folder_id = models.CharField(max_length=255, null=True, blank=True)
    folder_link = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "פרויקט"
        verbose_name_plural = 'פרויקטים'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    @property
    def budget(self):
        budgets = self.budgets.filter(project=self, is_active=True).first()
        amount = 0
        qty = 0
        if not budgets:
            return {
                'hours': 0,
                'amount': 0
            }
        if self.service.budget_type == 'fix':
            amount = amount + (budgets.qty * budgets.price)
        else:
            qty = qty + budgets.qty
            amount = amount + (budgets.qty * budgets.price) 
        
        budget = {
            'hours': qty,
            'amount': amount
        }
        return budget
    
    @property
    def usage(self):
        budget = ProjectBudget.objects.filter(project=self, is_active=True).first()
        return budget.reported_hours
    
    @property
    def budget_remaining(self):
        amount = self.budget.get('hours') - self.usage
        if self.budget.get('hours') == 0:
            percent = 0
        else:
            percent = self.usage / self.budget.get('hours')
        reminder = {
            'amount': amount,
            'percent': int(percent*100),
        }
        return reminder
    
    @property
    def timesheets(self):
        from activities.models import Timesheet
        return Timesheet.objects.filter(task__in=self.tasks.all())


    @property
    def get_drive_folder_link(self):
        url = f"https://workdrive.zoho.com/p42gl95b95c05518441b2b0f6ae441bb17051/teams/p42gl95b95c05518441b2b0f6ae441bb17051/ws/{self.customer.drive_folder_id}/folders/{self.folder_id}"
        return url



class ProjectBudget(models.Model):

    name = models.CharField(max_length=255)
    qty = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    is_active = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "תקציב פרויקט"
        verbose_name_plural = 'תקציבי פרויקטים'
        ordering = ['-created_at']

    def __str__(self):
        return f'תקציב עבור {self.project.name}'
    
    @property
    def total_price(self):
        return self.qty * self.price
    
    @property
    def reported_hours(self):
        timesheets = self.timesheets.all()
        amount = sum([x.hours for x in timesheets])
        return amount
