# Import
import json
from rest_framework import serializers

# Import utilities function
from encoder.models import Review

class ReviewListSerializer(serializers.ModelSerializer):
    # Use fields
    submission_timestamp        = serializers.DateTimeField(source='created_at')
    indexing_status             = serializers.CharField(source='index_status')
    start_indexing_timestamp    = serializers.DateTimeField(source='job_started_at')
    indexing_time_spent         = serializers.SerializerMethodField()
    current_page_index          = serializers.SerializerMethodField()

    # Return fields
    class Meta:
        model = Review
        fields = [
            'id',
            'name',
            'submission_timestamp',
            'indexing_status',
            'start_indexing_timestamp',
            'indexing_time_spent',
            'screening_status',
            'current_page_index'
        ]

    def get_indexing_time_spent(self, obj):
        if obj.job_started_at and obj.job_ended_at:
            total_seconds = (obj.job_ended_at - obj.job_started_at).total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        return None

    def get_current_page_index(self, obj):
        return obj.current_screening_page - 1 if obj.current_screening_page else None
    

# class ReviewSerializer(serializers.Serializer):
#     # Use fields
#     dataset_name                = serializers.CharField(source='name')
#     screening_progress_pannel   = serializers.CharField(source='screening_status')
#     query_pannel                = serializers.JSONField(source='pico_query')
#     screening_pannel            = serializers.SerializerMethodField()

#     def get_screening_pannel(self, obj):
#         # Assumes ranking_pages is a list and we want the first item
#         screen_pannel_rank = obj.ranking_pages[0]

#         # Mapping pmids
#         pmids = obj.corpus.pmids
#         for i in screen_pannel_rank["in_page_docs"]:
#             i["corpus"] = pmids.get(i["pmid"])

#         return screen_pannel_rank
class ReviewSerializer(serializers.Serializer):
    # Define serializer fields
    dataset_name                = serializers.CharField(source='name')
    screening_progress_pannel   = serializers.CharField(source='screening_status')
    query_pannel                = serializers.JSONField(source='pico_query')
    screening_pannel            = serializers.SerializerMethodField()

    def get_screening_pannel(self, obj):
        # Get page_index from the serializer context
        page_index  = self.context.get('page_index')
        single_page = self.context.get('single_page', True)

        if page_index is None:
            raise ValueError("page_index is required in the serializer context.")

        # Access the relevant ranking page
        ranking_pages = obj.ranking_pages
        if page_index >= len(ranking_pages) or page_index < 0:
            raise IndexError(f"page_index {page_index} is out of range for ranking_pages.")

        if single_page:
            screen_pannel_rank = ranking_pages[page_index]["in_page_docs"]
        else:
            screen_pannel_rank = []  # start from page 0 to page n
            for i in ranking_pages[0:page_index+1]:
                screen_pannel_rank.extend(i["in_page_docs"])

        # Map pmids
        pmids = obj.corpus.pmids
        for doc in screen_pannel_rank:
            doc["corpus"] = pmids.get(doc["pmid"])

        return screen_pannel_rank