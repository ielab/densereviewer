# Import
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APIRequestFactory, force_authenticate
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now
from urllib.parse import quote

import logging, os, traceback, json, shutil, asyncio
from time import time

logging = logging.getLogger(__name__)

# Import utilities function
from encoder.utils import *
from encoder.models import Corpus, Review
from encoder.serializers import ReviewListSerializer, ReviewSerializer

# Import Celery tasks
from app_utils.tasks        import init_indexing
from app_utils.re_ranking   import re_ranking, send_message_to_websocket

# Import Max's function
from app_utils.max.api_routing import parse_corpus, preview_corpus, corpus_converter, parse_query, export_by_judgment

# Create your views here.
class InitialRequestView(APIView):
    # Permission
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            msg = "The initial request was successful after the backend service started."
            logging.info(msg)
            return JsonResponse(data={"message": msg, "data": None}, status=status.HTTP_200_OK)
        
        except Exception as error:
            logging.error(f"{error}\n{traceback.format_exc()}")
            return JsonResponse({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileUploadView(APIView):
    # Permission
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle file upload.
            @body       nbib_file       File        A .nbib file
            @return     JsonResponse    Success message including the created corpus object
        """
        try:
            # Upload file
            nbib_file = request.FILES.get("nbib_file", None)
            corpus_obj = None

            # Format user id
            format_user_id = f"u{request.user.id:0{5}d}"

            # Create user's directory
            creat_user_dir(user=request.user, format_user_id=format_user_id)

            # Clean user temp folder (clear temp files after 24 hr.)
            clear_temp_folder(user=request.user, format_user_id=format_user_id)

            # Validate .nbib file & check duplicated in temp
            validate_upload_file(format_user_id=format_user_id, nbib_file=nbib_file)

            # Create new Corpus
            corpus_obj = Corpus.objects.create(user = request.user, status = "active")
            format_corpus_id = f"c{corpus_obj.id:0{5}d}"

            # Save file into database and local storage
            path_to_temp_file, save_corpus_filename, upload_folder = save_temp_file(
                user=request.user, 
                format_user_id=format_user_id, 
                format_corpus_id=format_corpus_id, 
                nbib_file=nbib_file
            )
           
            # Logging
            logging.info(f"User({request.user}) successfully uploaded nbib file ({nbib_file.name}) to temporarily folder.")

            # Call Max's function
            if settings.BYPASS_EXTERNAL_SERVICE:

                # Save file to corpus folder (move from temp)
                parse_corpus(corpus_nbib_path=path_to_temp_file, corpus_file=save_corpus_filename)

                # Hash corpus path
                hash_corpus = hash_blake2s_32digit(key=str(request.user.id), value=save_corpus_filename)

                # Preview corpus
                preview = preview_corpus(path_to_temp_file, 1)[0]

                # Save path file into database
                corpus_obj.hash_corpus_path = hash_corpus
                corpus_obj.real_corpus_path = save_corpus_filename
                corpus_obj.corpus_first_entry = preview
                corpus_obj.save()

                # Validate unique pmid in uploaded file
                validate_unique_pmid(corpus_path=save_corpus_filename)

                # Successful message
                msg = f"Successfully insert corpus({corpus_obj.id}) into database."
                logging.info(msg)

                # Move file from temp
                # os.remove(path_to_temp_file)
                shutil.move(path_to_temp_file, upload_folder)
                logging.info(f"Move file('{path_to_temp_file}') from temp to {upload_folder}.")

                # Create corpus for tevatron
                docid2pmid, corpus4tevatron, pmids = corpus_converter(corpus_path=save_corpus_filename)
                
                # Save corpus for tevatron into database
                corpus_obj.pmids            = pmids
                corpus_obj.corpus4tevatron  = "\n".join([json.dumps(record) for record in corpus4tevatron])       # Convert list of dictionaries to JSONL string
                corpus_obj.docid2pmid       = docid2pmid
                corpus_obj.save()

            # Returning data
            data ={
                "preview_uploaded_corpus": {"id": corpus_obj.id, "corpus_first_entry": preview},
                "total_documents": len(corpus4tevatron)
            }

            # Return
            return JsonResponse(
                data={"message": msg, "data": data}, 
                status=status.HTTP_200_OK
            )


        # Exception ValueError
        except ValueError as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logging
            logging.error(f"user({request.user}) failed to upload nbib file: {error}")
            return JsonResponse(
                {"error": f"user({request.user}) failed to upload nbib file: {error}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exception FileExistsError
        except FileExistsError as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logging
            logging.error(f"user({request.user}) failed to upload nbib file: {error}")
            return JsonResponse(
                {"error": f"user({request.user}) failed to upload nbib file: {error}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exception Other error
        except Exception as error:
            # Update corpus status
            if corpus_obj:
                corpus_obj.status = "upload_failed"
                corpus_obj.save()

            # logging
            logging.error(f"Error while uploading nbib file")
            return JsonResponse(
                {"error": f"Error while uploading nbib file: {error}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    
    def delete(self, request):
        """
        Delete corpus row and its files from Amazon S3 bucket
            @query_param        corpus_id           Corpus ID
            @return             JsonResponse        Success message
        """
        try:
            corpus_id = request.query_params.get("corpus_id")

            # Set the corpus status to 'user_delete'
            corpus_obj = Corpus.objects.get(id=corpus_id)
            corpus_obj.status = "user_delete"
            corpus_obj.save()

            # User corpus directory
            user_corpus_dir = os.path.join(f"{settings.MOUNT_CORPUS_PATH}", f"u{request.user.id:0{5}d}", "corpus", f"c{corpus_obj.id:0{5}d}", "upload")

            # Delete the files from local storaage
            corpus_dir = corpus_obj.real_corpus_path

            # Delete the files from local storage
            for f in [user_corpus_dir, corpus_dir]:
                remove_file_from_local_storage(f)

            # Message
            msg = f"User({request.user.id}) has deleted corpus({corpus_id}) of user({corpus_obj.user.id})."
            logging.info(msg)
            return JsonResponse({"message": msg}, status=status.HTTP_200_OK)

        except Corpus.DoesNotExist as error:
            logging.error(
                f"corpus({corpus_id}) does not exist for user({request.user.id}): {error}"
            )
            return JsonResponse({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            logging.error(
                f"Couldn't delete corpus({corpus_id}) of user({request.user.id}): {error}\n{traceback.format_exc()}"
            )
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatasetCreation(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Dataset creation.
            @body       pico            Object              The group of people or individuals being studied | 
                                                            The treatment, exposure, or action being studied | 
                                                            The alternative or standard invention being used for comparison | 
                                                            The result or effect being measured   
            @return     JsonResponse    Success message
        """
        try:
            # Data from request
            corpus_id           = request.data.get('corpus_id', None)
            dataset_name        = request.data.get('dataset_name', None)
            pico_query          = request.data.get('pico_query', None)
            show_docs_per_page  = request.data.get('show_docs_per_page', 25)
            review_obj = None

            # Query corpus
            corpus_obj = Corpus.objects.get(id=corpus_id, user=request.user)
            logging.info(f">>> real corpus path: {corpus_obj.real_corpus_path}")

            # Validated dataset name duplicate
            is_duplicated = Review.objects.filter(name=dataset_name, user=request.user)
            if is_duplicated:
                raise ValueError(f"The collection name({dataset_name}) is duplicated.")

            # Get number of queue
            n_queue = get_number_of_queue(queue_name=settings.QUEUE_NAME_1)

            # Create dataset
            review_obj = Review.objects.create(
                user                    = request.user,
                corpus                  = corpus_obj,
                name                    = dataset_name,
                index_status            = "queued",
                screening_status        = "not_start",
                show_docs_per_page      = show_docs_per_page,
                pico_query              = pico_query,       # json fields
                pos_at_waiting_queue    = n_queue,          # job
                job_queued_at           = now(),
            )
            review_obj.save()

            # Start celery job
            # User corpus directory
            user_corpus_dir = os.path.join(f"{settings.MOUNT_CORPUS_PATH}", f"u{request.user.id:0{5}d}", "corpus", f"c{review_obj.corpus.id:0{5}d}")

            # Load jsonl (corpus4tevatron)
            corpus4tevatron = [json.loads(line) for line in review_obj.corpus.corpus4tevatron.splitlines()]

            # Save corpus4tevatron as json file
            corpus4tevatron_path = save_temporary_file(user_corpus_dir=user_corpus_dir, data=corpus4tevatron, input_type="corpus4tevatron")

            # Call Max's function
            if settings.BYPASS_EXTERNAL_SERVICE:
                # Parse PICO query
                query_path      = os.path.join(user_corpus_dir, "query.json")
                parse_query(pico_data=pico_query, output_path=query_path)

                # Get intial ranking (Call Celery)
                init_indexing.delay(
                    review_id=review_obj.id,
                    show_docs_per_page=show_docs_per_page,
                    query_path=query_path,
                    corpus4tevatron_path=corpus4tevatron_path,
                    user_corpus_dir=user_corpus_dir,
                    init_rank_dir=os.path.join(user_corpus_dir, "tevatron_results")
                )
            
            # Message
            msg = f"Your corpus (ID: {corpus_obj.id}) with the name '{review_obj.name}' has been queued."
            logging.info(msg)

            # Return
            return JsonResponse(data = {"message": msg, "data": None}, status=status.HTTP_200_OK)
        
        except ValueError as error:
            # Message
            msg = f"Invalid input for dataset creation: {error}"

            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = msg

            # Logging and return
            logging.error(msg)
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = str(error)

            logging.error(
                f"Couldn't create dataset for '{dataset_name}' of user({request.user.id}): {error}\n{traceback.format_exc()}"
            )
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user's dataset list
        """
        try:
            # Query review object
            review_obj = Review.objects.filter(user=request.user).order_by('id')

            # Serialize the sorted data
            serializer_review = ReviewListSerializer(review_obj, many=True)

            # Logging and return
            msg = f"Got dataset list of user({request.user.id})"
            logging.info(msg)
            return JsonResponse(
                {
                    "message": msg,
                    "data": serializer_review.data
                },
                status=status.HTTP_200_OK,
                safe=False
            )

        except Exception as error:
            logging.error(f"Couldn't get dataset list for user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewDataset(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Parse input data
            review_id   = request.data.get('review_id')

            # Query review object
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()

            # Current screening page
            current_screening_page = review_obj.current_screening_page - 1

            # Parse input data
            page_index  = int(request.data.get('page_index', current_screening_page))

            # Check if review exists
            if not review_obj:
                logging.error(f"Review({review_id}) does not exist for user({request.user.id})")
                return JsonResponse({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update screening status
            if page_index == 0:
                review_obj.started_screening_at = now()
                review_obj.save()

            # Validate, is review complete?
            if review_obj.screening_status == "finished":
                msg = f"User ({request.user.id}) has already finished reviewing the dataset ({review_obj.name})."
                logging.warning(msg)
                return JsonResponse(data={"message": msg, "data": None}, status=status.HTTP_200_OK)
            
            else:
                review_obj.screening_status = "screening"
                review_obj.save()

            # Serialize the data
            serializer_review = ReviewSerializer(review_obj, context={"page_index": page_index})
            data = serializer_review.data

            # Dashboard data
            dashboard_data = summary_data(review_obj=review_obj, page_index=page_index, show_total=True)

            # Return data
            data["dashboard_data"] = dashboard_data

            # Get number of all pages
            data["total_number_of_pages"] = get_all_pages(review_obj=review_obj)

            # Return current page index
            data["current_page_index"] = current_screening_page

            # Message
            msg = f"Got review dataset for user({request.user.id}) with page index({page_index})."
            logging.info(msg)

            # Return
            return JsonResponse(
                data={"message": msg, "data": data},
                status=status.HTTP_200_OK
            )
        
        except Exception as error:
            logging.error(f"Couldn't get review dataset for user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": str(error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UpdateFeedbackView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse input data
        review_id           = request.data.get('review_id')
        page_index          = int(request.data.get('page_index'))
        in_page_rank_index  = int(request.data.get('in_page_rank_index'))
        pmid                = request.data.get('pmid')
        feedback            = request.data.get('feedback')

        try:
            if not all([review_id, str(page_index), str(in_page_rank_index), pmid, feedback]):
                msg = "All fields (review_id, page_index, in_page_rank_index, pmid, feedback) are required."
                logging.error(msg)
                raise ValueError(msg)

            # Query the Review model for user_id and review_id
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()
            
            # Updated feedback
            previous_feedback = update_feedback(
                review_obj=review_obj,
                page_index=page_index,
                in_page_rank_index=in_page_rank_index,
                pmid=pmid, 
                feedback=feedback
            )
            
            # Updated page screening log
            update_page_screening_log(review_obj=review_obj, page_index=page_index, is_done=False)

            # Updated review type
            updated_review_type(review_obj=review_obj, pmid=pmid, previous_feedback=previous_feedback, feedback=feedback)

            # Dashboard data
            dashboard_data = summary_data(review_obj=review_obj, page_index=page_index)

            # Logging and return
            msg = f"Feedback updated for pmid({pmid}), page index({page_index}), review({review_id}) of user({request.user.id}) successfully."
            logging.info(msg)
            return JsonResponse(data={"message": msg, "data": dashboard_data}, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            msg = "Review not found for the given user_id and corpus_id."
            logging.error(msg)
            return JsonResponse(data={"error": msg}, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError as error:
            msg = str(error)
            logging.error(msg)
            return JsonResponse({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as error:
            msg = str(error)
            logging.error(f"{msg}\n{traceback.format_exc()}")
            return JsonResponse(data={"error": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RerankingView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse input data
        review_id   = request.data.get('review_id')
        page_index  = int(request.data.get('page_index'))
        token       = request.headers.get('Authorization')      # Access the Authorization header
        
        try:
            # Query review object
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()
            ranking_pages = review_obj.ranking_pages

            # Validate page index
            if page_index >= len(ranking_pages) or page_index < 0:
                msg = f"page_index {page_index} is out of range for ranking_pages."
                logging.error(msg)
                raise IndexError(msg)
            
            # Validate the page that has already been re-ranked
            if page_index < len(ranking_pages) - 1:
                # Message
                msg = f"The page {page_index+1} (with page index {page_index}) has already been re-ranked."
                logging.warning(msg)

                # Create a factory request for internal call
                factory = APIRequestFactory()
                internal_request = factory.post('/review-dataset/', data={"review_id": review_id, "page_index": page_index+1})
                
                # Force authentication for the internal request
                force_authenticate(internal_request, user=request.user)

                # Call ReviewDataset's post method directly
                response = ReviewDataset.as_view()(internal_request)
                
                # Send a message to the Celery notifications channel
                asyncio.run(send_message_to_websocket(token=token.replace("Token ", ""), message=review_obj.index_status))

                # Return existing data
                return response

            # Validate, is previous review complete?
            if validate_prev_review(prev_review=ranking_pages[page_index]["in_page_docs"]):
                msg = f"User ({request.user.id}) has not finished reviewing the previous({page_index+1}) page of dataset ({review_obj.name})."
                logging.error(msg)
                return JsonResponse({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        
            # Updated page screening log
            update_page_screening_log(review_obj=review_obj, page_index=page_index, is_done=True)

            # User corpus directory
            user_corpus_dir = os.path.join(f"{settings.MOUNT_CORPUS_PATH}", f"u{request.user.id:0{5}d}", "corpus", f"c{review_obj.corpus.id:0{5}d}")

            # Get number of queue
            n_queue = get_number_of_queue(queue_name=settings.QUEUE_NAME_2)

            # Update review object
            review_obj.index_status = "queued"
            review_obj.pos_at_waiting_queue = n_queue
            review_obj.job_queued_at = now()
            review_obj.save()

            # Call Max's function
            if settings.BYPASS_EXTERNAL_SERVICE:
                # Model name
                model_name = "biolinkbert_128_256_11"

                # Path to files
                index_path = os.path.join(user_corpus_dir, "indexes", model_name, f"r{review_obj.id:05d}")
                query_embedding_path = os.path.join(user_corpus_dir, "query_encode", f"r{review_obj.id:05d}", model_name, f"r{review_obj.id:05d}_query_pico.pkl")

                # Reranking
                re_ranking.delay(
                    token=token.replace("Token ", ""),
                    review_id=review_id,
                    index_path=index_path,
                    query_embedding_path=query_embedding_path,
                )
            
                # Message
                msg = f"Your corpus({review_obj.corpus.id}) with the name '{review_obj.name}' has been re-ranking queued."
                logging.info(msg)

            # Return
            return JsonResponse(data = {"message": msg, "data": None}, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            msg = "Review not found for the given user_id and corpus_id."
            logging.error(msg)
            return JsonResponse(data={"error": msg}, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError as error:
            # Message
            msg = f"Invalid input for re-ranking: {error}"

            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = msg

            # Logging and return
            logging.error(msg)
            return JsonResponse({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            # Update review status
            if review_obj:
                review_obj.index_status = "indexing_error"
                review_obj.indexing_error_msg = str(error)

            logging.error(f"Couldn't re-ranking for '{review_obj.name}' of user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReviewProgessView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse input data
        review_id   = request.data.get('review_id')
        page_index  = int(request.data.get('page_index', 0))
        is_finished = int(request.data.get('is_finished', 0))
        
        try:
            # Query review object
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()

            # Check if review exists
            if not review_obj:
                logging.error(f"Review({review_id}) does not exist for user({request.user.id})")
                return JsonResponse({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

            # Validate, is previous review complete?
            if validate_prev_review(prev_review=review_obj.ranking_pages[page_index]["in_page_docs"]):
                msg = f"User ({request.user.id}) has not finished reviewing the previous({page_index+1}) page of dataset ({review_obj.name})."
                logging.error(msg)
                return JsonResponse({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate, is review complete?
            if is_finished:
                # Update review status
                review_obj.screening_status = "finished"
                review_obj.finished_screening_at = now()
                review_obj.save()

                # Massage
                msg = f"User ({request.user.id}) has finished reviewing the dataset ({review_obj.name})."
            
            else:
                # Update review paused screening
                review_obj.screening_status = "paused"
                review_obj.paused_screening_at = now()
                review_obj.save()

                # Massage
                msg = f"User ({request.user.id}) has paused reviewing the dataset ({review_obj.name})."

            # Serialize the data
            serializer_review = ReviewSerializer(review_obj, context={"page_index": page_index, "single_page": False})
            data = serializer_review.data

            # Dashboard data
            data["dashboard_data"] = summary_review_progress(data=data["screening_pannel"])

            # Message
            logging.info(msg)

            # Return
            return JsonResponse(
                data={"message": msg, "data": data},
                status=status.HTTP_200_OK
            )
        
        except Exception as error:
            logging.error(f"Couldn't get review dataset for user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": str(error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExportReviewProgessView(APIView):
    """
    API view to handle the export of review progress data.
    This view allows authenticated users to export review progress data based on the provided
    review ID, page index, judgment type, and export data. The exported data is saved as an NBIB
    file and a URL to the exported file is returned.
    Attributes:
        permission_classes (list): List of permission classes required to access this view.
    Methods:
        post(request):
            Handles the POST request to export review progress data.
            Parameters:
                request (Request): The HTTP request object containing the input data.
            Returns:
                JsonResponse: A JSON response containing the URL to the exported file or an error message.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse input data
        review_id       = request.data.get("review_id")
        page_index      = request.data.get("page_index", "full")
        judgment_type   = request.data.get("judgment_type", ["include", "maybe", "exclude"])
        export_data     = request.data.get("export_data", [])
        
        try:
            # Query review object
            review_obj = Review.objects.filter(id=review_id, user=request.user).first()

            # Check if review exists
            if not review_obj:
                logging.error(f"Review({review_id}) does not exist for user({request.user.id})")
                return JsonResponse({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get uploaded file
            input_ris_file = get_uploaded_file_path(user_id=request.user.id, corpus_id=review_obj.corpus.id)

            # Export file name
            formatted_date = now().strftime("%Y%m%d")
            formatted_judgment_type = "all" if judgment_type == ["include", "maybe", "exclude"] else "_".join(judgment_type)
            output_file_name = f"{formatted_date}_p{int(page_index)+1}_{formatted_judgment_type}.nbib"
        
            # Prepare export file
            user_corpus_dir     = os.path.join(f"{settings.MOUNT_CORPUS_PATH}", f"u{request.user.id:05d}", "corpus", f"c{review_obj.corpus.id:05d}")
            output_nbib_folder  = os.path.join(user_corpus_dir, "export", f"r{review_obj.id:05d}")
            output_nbib_file    = os.path.join(output_nbib_folder, output_file_name)

            # Create output folder
            os.makedirs(output_nbib_folder, exist_ok=True)
            
            # Export data
            export_by_judgment(
                docs=export_data,
                judgment_type=judgment_type,
                input_ris_file=input_ris_file,
                output_nbib_file=output_nbib_file
            )

            # Check if file exists
            if not os.path.exists(output_nbib_file):
                raise FileNotFoundError(f"Exported file not found: {output_nbib_file}")
            
            # Generate Nginx-served URL
            relative_path = output_nbib_file.replace(settings.MOUNT_CORPUS_PATH, "")
            export_url = f"exports{relative_path}"  # Prefix with '/exports' for Nginx
            export_url = export_url.replace("\\", "/")  # Ensure URL uses forward slashes
            export_url = quote(export_url)  # URL encode any special characters

            # Concat domain name
            export_url = f"https://{settings.ALLOWED_HOSTS[-1]}/{export_url}"
            
            # Return URL
            return JsonResponse(data={"url": export_url}, status=status.HTTP_200_OK)

        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            return JsonResponse({"error": "Exported file not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            logging.error(f"Couldn't export review dataset for user({request.user.id}): {error}\n{traceback.format_exc()}")
            return JsonResponse(
                {"error": str(error)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
