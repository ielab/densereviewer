from django.urls import path

from encoder.views import *

urlpatterns = [
    path('initial_request', InitialRequestView.as_view()),
    path('upload_corpus', FileUploadView.as_view()),
    path('dataset_creation', DatasetCreation.as_view()),
    path('get_review_list', ReviewList.as_view()),
    path('review_dataset', ReviewDataset.as_view()),
    path('update_feedback', UpdateFeedbackView.as_view()),
    path('re_ranking', RerankingView.as_view()),
    path('review_progress', ReviewProgessView.as_view()),
    path('export_review', ExportReviewProgessView.as_view())
]
