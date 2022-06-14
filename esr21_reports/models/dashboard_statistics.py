from django.db import models
from ..choices import STATISTICS_TYPE


class DashboardStatistics(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()
