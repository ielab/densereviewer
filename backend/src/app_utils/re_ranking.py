# Import
import os, logging, json, asyncio
from time import time
from datetime import datetime
from celery import shared_task
from redis.asyncio import Redis

# Import utilities from Django
from django.conf import settings
from django.utils.timezone import now

# Import DenseReviewer's Core functions
from app_utils.core.dense_ranker import InteractiveRanker

# Import utilities function
from encoder.models import Review

# Import configure logger
logging = logging.getLogger(__name__)

# Utility function
async def send_message_to_websocket(token, message):
    redis = await Redis.from_url(settings.REDIS_URL)
    await redis.publish('celery_notifications', json.dumps({'message': message, 'token': token, 'backup_policy': True}))

# Celery tasks
@shared_task(queue=settings.QUEUE_NAME_2)
def re_ranking(token, review_id, index_path, query_embedding_path):
    try:
        # Start timer
        start_time = time()
        logging.info(f"Start task: {datetime.now()}")

        # Query review object
        review_obj = Review.objects.get(id=review_id)

        # Update review field values
        review_obj.job_started_at = now()
        review_obj.index_status = "re-ranking"        # Change to "re-ranking"
        review_obj.save()

        # Train model path
        train_model_path="/app/backend/src/app_utils/max/trained_models/clef19_intervention/biolinkbert_128_256_11"

        # Re-rank
        ranker = InteractiveRanker(
            model_path=train_model_path,
            index_path=index_path,
            query_embedding_path=query_embedding_path,
            rocchio_params=[1.0, 1.0, 1.0]  # [alpha, beta, gamma]
        )

        # Generate new ranking page
        previous_ranking_page = review_obj.ranking_pages
        new_ranking = ranker.generate_ranking_pages(previous_ranking_page[-1])

        # Update ranking page
        previous_ranking_page.append(new_ranking)

        # Update current screening page
        review_obj.current_screening_page += 1

        # Update review field values
        review_obj.ranking_pages = previous_ranking_page
        review_obj.index_status = "re-rank_ready"       # Change to "re-rank_ready"
        review_obj.save()

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

        # Send a message to the Celery notifications channel
        asyncio.run(send_message_to_websocket(token=token, message=review_obj.index_status))