from django.db import models
from apps.core.models import BaseModel


class AnalysisResult(BaseModel):
    analysis = models.OneToOneField("analysis.Analysis", on_delete=models.CASCADE)
    data = models.JSONField()
    confidence = models.FloatField()
    verdict = models.CharField(max_length=50)

    class Meta:
        db_table = "results_analysis_results"
