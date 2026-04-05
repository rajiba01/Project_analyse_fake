from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.results.models import AnalysisResult
from apps.results.serializers import AnalysisResultSerializer


class ResultViewSet(ViewSet):
    def retrieve(self, request, pk=None):
        result = get_object_or_404(AnalysisResult, analysis_id=pk)
        serializer = AnalysisResultSerializer(result)
        return Response(serializer.data)
