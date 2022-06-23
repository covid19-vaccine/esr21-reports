from django.db import models
from edc_base.model_mixins import BaseUuidModel


class DashboardStatistics(BaseUuidModel):
    key = models.CharField(max_length=50)
    value = models.TextField()
