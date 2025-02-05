from django.db import models
from account.models import User

# Create your models here.
CORPUS_STATUSES = [
    ("active", "Active"),
    ("admin_delete", "Deleted by Admin"),
    ("user_delete", "Deleted by User"),
    ("upload_failed", "Upload Failed"),
]

INDEX_STATUSES = [
    ("queued", "Queued"),
    ("indexing", "Indexing"),
    ("index_ready", "Indexing Ready"),
    ("re-ranking", "Re-ranking"),
    ("re-ranking_ready", "Re-ranking ready"),
    ("archived", "Archived"),
    ("indexing_error", "Indexing Error")
]

SCREENING_STATUSES = [
    ("not_start", "Not Start"),
    ("screening", "Screening"),
    ("paused", "Paused"),
    ("finished", "Finished"),
]

class Corpus(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    status              = models.CharField(max_length=32, choices=CORPUS_STATUSES)
    hash_corpus_path    = models.CharField(max_length=32, default=None, null=True)
    real_corpus_path    = models.CharField(max_length=100, default=None, null=True)
    corpus_first_entry  = models.TextField(max_length=1000, default=None, null=True)
    pmids               = models.JSONField(default=None, null=True)
    corpus4tevatron     = models.TextField(default=None, null=True)
    docid2pmid          = models.TextField(default=None, null=True)
    # default fields
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'corpus'


class Review(models.Model):
    user                    = models.ForeignKey(User, on_delete=models.CASCADE)
    corpus                  = models.ForeignKey(Corpus, on_delete=models.CASCADE)
    name                    = models.CharField(max_length=150)
    index_status            = models.CharField(max_length=32, choices=INDEX_STATUSES)
    screening_status        = models.CharField(max_length=32, choices=SCREENING_STATUSES, default="not_start")
    current_screening_page  = models.IntegerField(default=1, null=True)
    show_docs_per_page      = models.IntegerField(default=25, null=False)
    # json fields
    pico_query              = models.JSONField(default=None, null=True)
    ranking_pages           = models.JSONField(default=None, null=True)
    page_screening_log      = models.JSONField(default=None, null=True)
    include_docs            = models.JSONField(default=None, null=True)
    exclude_docs            = models.JSONField(default=None, null=True)
    maybe_docs              = models.JSONField(default=None, null=True)
    user_interaction        = models.JSONField(default=None, null=True)
    # reviewing time
    started_screening_at    = models.DateTimeField(default=None, null=True)
    paused_screening_at     = models.DateTimeField(default=None, null=True)
    finished_screening_at   = models.DateTimeField(default=None, null=True)
    # job
    pos_at_waiting_queue    = models.IntegerField()
    job_queued_at           = models.DateTimeField(auto_now_add=True)
    job_started_at          = models.DateTimeField(default=None, null=True)
    job_ended_at            = models.DateTimeField(default=None, null=True)
    indexing_error_msg      = models.TextField(default=None, null=True)
    # default fields
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)
    archived_at             = models.DateTimeField(default=None, null=True)

    class Meta:
        db_table = 'review'