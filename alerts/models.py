from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class AlertType(models.Model):

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "סוג התראה"
        verbose_name_plural = "סוגי התראה"

    def __str__(self):
        return self.name


class AlertSettings(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE)

    created_email = models.BooleanField(default=False)
    updated_email = models.BooleanField(default=False)
    deleted_email = models.BooleanField(default=False)

    created_in_app = models.BooleanField(default=False)
    updated_in_app = models.BooleanField(default=False)
    deleted_in_app = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "הגדרות התראות"
        verbose_name_plural = "הגדרות התראות"
        unique_together = ('user', 'alert_type')

    def __str__(self):
        return self.alert_type.name

