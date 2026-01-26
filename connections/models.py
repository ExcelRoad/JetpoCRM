from django.db import models

class Workdrive(models.Model):

    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255, unique=True)

    is_connected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Workdrive Connection'

    def save(self, *args, **kwargs):
        # Make sure only one is existing
        if Workdrive.objects.exists() and not self.id:
            current_workdrive = Workdrive.objects.first()
            self.id = current_workdrive.id
        super(Workdrive, self).save(*args, **kwargs)


class Sumit(models.Model):

    company_id = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=255, unique=True)
    customer_folder_id = models.CharField(max_length=255, unique=True)

    is_connected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Sumit Connection'
    
    def save(self, *args, **kwargs):
        # Make sure only one is existing
        if Sumit.objects.exists() and not self.id:
            current_sumit = Sumit.objects.first()
            self.id = current_sumit.id
        super(Sumit, self).save(*args, **kwargs)
