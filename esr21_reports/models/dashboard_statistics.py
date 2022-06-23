from django.db import models


class DashboardStatistics(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()
