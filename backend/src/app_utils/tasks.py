# Import
import os, logging, json, subprocess
from time import time
from datetime import datetime
from celery import shared_task

# Import utilities from Django
from django.conf import settings
from django.db.models import F, Case, When, Value
from django.utils.timezone import now

# Import Max's function
from app_utils.max.tevatron_pipe    import dpr_pipeline
from app_utils.max.api_routing      import get_init_ranking
from app_utils.max.pyserini_index   import index_corpus

# Import utilities function
from encoder.models import Review

# Import configure logger
logging = logging.getLogger(__name__)

# Utility function
# Save temporary json files
def save_temporary_file(user_corpus_dir, pico_query, corpus4tevatron):
    # Temporary save query
    query_path = os.path.join(user_corpus_dir, "query.json")
    with open(query_path, "w") as f:
        json.dump(pico_query, f)
    logging.info(f"Create temporary file for query.json: {query_path}")
    
    # Temporary save corpus4tevatron
    corpus4tevatron_path = os.path.join(user_corpus_dir, "corpus4tevatron.jsonl")
    with open(corpus4tevatron_path, "w") as f:
        for record in corpus4tevatron:
            f.write(json.dumps(record) + "\n")  # Serialize each record and add a newline
    logging.info(f"Create temporary file for corpus4tevatron.jsonl: {corpus4tevatron_path}")

    return query_path, corpus4tevatron_path

# Save corpus4tevatron (jsonl)
def save_corpus4tevatron(corpus4tevatron, output_path):
    with open(output_path, 'w') as outfile:
        for study in corpus4tevatron:
            jsonl_string = json.dumps(study)
            outfile.write(jsonl_string + '\n')

# Remove temporary json files
def remove_temporary_file(remove_lst):
    # Remove temporary files
    for f in remove_lst:
        os.remove(f)
        logging.info(f"Remove temporary file: {f}")

# Update number of queue
def update_queue():
    # Update number_of_queue, decrement by 1, minimum value of 0
    Review.objects.filter(index_status='queued').update(
        pos_at_waiting_queue=Case(
            # If decrementing results in a value less than 0, set to 0
            When(pos_at_waiting_queue__gt=0, then=F('pos_at_waiting_queue') - 1),
            default=Value(0)  # Use 0 if the above condition is not met (i.e., number_of_queue <= 0)
        )
    )

# Celery tasks
@shared_task(queue=settings.QUEUE_NAME_1)
def init_indexing(review_id, show_docs_per_page, query_path, corpus4tevatron_path, user_corpus_dir, init_rank_dir):
    # Query review object
    review_obj = Review.objects.get(id=review_id)
    try:
        # Start timer
        start_time = time()
        logging.info(f"Start task: {datetime.now()}")

        # Update number of queue
        update_queue()

        # Update review field values
        review_obj.job_started_at = now()
        review_obj.index_status = "indexing"
        review_obj.save()

        # Train model path
        train_model_path="/app/backend/src/app_utils/max/trained_models/clef19_intervention/biolinkbert_128_256_11"

        # Create directory for saving the initial ranking result
        os.makedirs(init_rank_dir, exist_ok=True)

        # # Temporary save query and corpus4tevatron
        # query_path, corpus4tevatron_path = save_temporary_file(user_corpus_dir, pico_query, corpus4tevatron)

        # Defind corpus encoded directory
        corpus_encode_dir=os.path.join(user_corpus_dir, "corpus_encode")

        # Get initial ranking
        init_rank_path = dpr_pipeline(
            train_model_path=train_model_path,
            project_id=f"r{review_id:05d}",
            query_path=query_path,
            query_encode_dir=os.path.join(user_corpus_dir, "query_encode"), 
            corpus_path=corpus4tevatron_path,
            corpus_encode_dir=corpus_encode_dir,
            init_rank_dir=init_rank_dir
        )

        # Remove temporary files
        remove_temporary_file(remove_lst=[query_path])

        # Get initial ranking
        # init_rank_path: /opt/dense-review/user-corpus/u00002/corpus/c00044/tevatron_results/35/biolinkbert_128_256_11/35_rank_pico.txt
        ranking_pages = get_init_ranking(init_rank_path, None, show_docs=show_docs_per_page)
        review_obj.ranking_pages = ranking_pages
        review_obj.index_status = "index_ready"       # Change to "index_ready"
        review_obj.save()

        # Run pyserini index
        print(corpus4tevatron_path)
        corpus_name = f"r{review_obj.id:05d}"
        index_corpus(
            corpus_path=corpus4tevatron_path, 
            model_path=train_model_path, 
            dynamic_save_path=user_corpus_dir, 
            review_id=corpus_name
        )

    except Exception as e:
        # Error message
        error_msg = str(e)

        # Update review field values
        review_obj.indexing_error_msg = error_msg
        review_obj.index_status = "indexing_error"
        review_obj.save()

        # Logging
        logging.error(f"Error message: {error_msg}")

    finally:
        # Stop timer
        end_time = time()
        elapsed_time = (end_time - start_time) / 60

        # Update review field values
        review_obj.job_ended_at = now()
        review_obj.save()

        # Logging
        logging.info(f"End task: {datetime.now()}")
        logging.info(f"Total processing time: {elapsed_time} minutes.")
        logging.info("---" * 25)
        logging.info("\n")