# import
import os, logging, hashlib, requests, json, math
from time import sleep, time
from datetime import datetime, timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from django.conf import settings
from collections import defaultdict
from hashlib import sha256

# import utilities function
from account.models import User
from encoder.models import Corpus

logging = logging.getLogger(__name__)

# functions
def get_utc_datetime():
    # Get the current UTC datetime
    return datetime.now(timezone.utc).isoformat()


def creat_user_dir(user, format_user_id):
    """
    Create temp and corpus directory for each user.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
    """
    # Create user directory if not exist
    for dir in ["temp", "corpus"]:

        # Is directory exist
        user_dir = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, dir)
        if not os.path.exists(user_dir):
            # Create directory
            os.makedirs(user_dir)
            logging.info(f"Create folder '{user_dir}' for user({user.username}).")


def hash_blake2s_32digit(key, value):
    """
    Hash the value and return the hash value in hexadecimal format 32-bit long.
        @param      key         key to be hashed
        @param      value       value to be hashed
        @return     hash value in hexadecimal format
    """
    hash_obj = hashlib.blake2s(key.encode("utf-8"), digest_size=16)
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def validate_upload_file(format_user_id: int, nbib_file: str):
    """
    Validate upload file.
        @param      format_user_id      string      An user id who upload the file.
        @param      nbib_file           string      A dataset file.
    """
    # Get file extension
    file_extension = nbib_file.name.split(".")[-1]

    # Real corpus path
    real_corpus_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "temp", nbib_file.name)

    # Validate .nbib file
    if not (file_extension in ["nbib", "ris"]):
        raise ValueError(f"Invalid file format: .{file_extension}. Please upload a file with a .nbib or .ris extension.")

    # Validate duplicate file (in temp)
    if os.path.exists(real_corpus_path):
        raise FileExistsError(f"File with the same name('{nbib_file.name}') already exists. Please rename the file before upload again.")


def validate_unique_pmid(corpus_path: str):
    seen_pmids = set()
    with open(corpus_path, 'r') as infile:
        corpus_data = json.load(infile)

        for study in corpus_data:
            pmid = study.get('pmid')
            if pmid in seen_pmids:
                raise ValueError(f"Uploaded file has duplicated pmid: {pmid}")
            seen_pmids.add(pmid)


def save_temp_file(user: object, format_user_id: str, format_corpus_id: str, nbib_file: str):
    """
    Save upload .nbib file.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
        @param      format_corpus_id    string      Format corpus id.
        @param      nbib_file           string      A corpus file.
    """
    # Sanitize the filename to prevent directory traversal
    safe_filename = get_valid_filename(nbib_file.name)
    save_path = os.path.join("user-corpus", format_user_id, "temp", safe_filename)

    # path to save corpus.json file
    save_corpus_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "corpus", format_corpus_id)
    save_corpus_filename = os.path.join(save_corpus_path, "corpus.json")
    os.makedirs(save_corpus_path, exist_ok=True)

    # Create upload folder
    upload_folder = os.path.join(save_corpus_path, "upload")
    os.makedirs(upload_folder, exist_ok=True)

    # Save file into local storage
    default_storage.save(save_path, ContentFile(nbib_file.read()))

    return save_path, save_corpus_filename, upload_folder


def get_uploaded_file_path(user_id, corpus_id):
    user_upload_dir = os.path.join(settings.MOUNT_CORPUS_PATH, f"u{user_id:05d}", "corpus", f"c{corpus_id:05d}", "upload")
    return [os.path.join(user_upload_dir, i) for i in os.listdir(user_upload_dir)][0]


def clear_temp_folder(user, format_user_id: str):
    """
    Remove nbib file in temporarity that store more than 24 hr.
        @param      user                object      An user's who upload the file.
        @param      format_user_id      string      Format user id.
    """
    # Temp path
    temp_path = os.path.join(settings.MOUNT_CORPUS_PATH, format_user_id, "temp")
    now = datetime.now()

    # List all files and directories in the specified path
    files = os.listdir(temp_path)
    for f in files:
        # File path
        file_path = os.path.join(temp_path, f)

        # Get the time of last modified
        modified_time = os.path.getmtime(file_path)

        # Converting the time in seconds to datetime
        last_modified = datetime.fromtimestamp(modified_time)

        # Calculate difference hour
        diff = (now - last_modified).total_seconds() // 3600

        # Remove file if store in temp >= 24 hr
        if diff >= 24:
            os.remove(file_path)
            logging.info(f"Remove user({user})'s previously uploaded file, because this file({file_path}) is older than 24 hours.")


def get_number_of_queue(queue_name):

    rabbitmq_user       = settings.RABBITMQ_DEFAULT_USER
    rabbitmq_password   = settings.RABBITMQ_DEFAULT_PASS

    sleep(0.75)
    response = requests.get(
        f"http://rabbitmq:15672/api/queues/%2F/{queue_name}",
        auth=(rabbitmq_user, rabbitmq_password),
    )

    queue_info = response.json()
    return queue_info["messages"]


# Save temporary JSON files
def save_temporary_file(user_corpus_dir, data, input_type):
    """
    Saves data to a temporary file in the specified directory.

    Parameters:
        user_corpus_dir (str): Directory where the file should be saved.
        data (dict or list): Data to be saved.
        input_type (str): Type of input to determine file name and format.

    Returns:
        str: Path to the saved file.
    """
    # Define file name based on input type
    file_mapping = {
        "pico_query": "query.json",
        "corpus4tevatron": "corpus4tevatron.jsonl"
    }
    if input_type not in file_mapping:
        raise ValueError(f"Unsupported input_type: {input_type}")

    save_path = os.path.join(user_corpus_dir, file_mapping[input_type])

    # Save data
    with open(save_path, "w") as f:
        if input_type == "pico_query":
            json.dump(data, f)
        else:  # "corpus4tevatron"
            f.writelines(json.dumps(record) + "\n" for record in data)

    logging.info(f"Created temporary file: {save_path}")
    return save_path


def update_feedback(review_obj, page_index, in_page_rank_index, pmid, feedback):
    # Update user interaction
    def update_user_interact(previous_feedback, study):
        # Retrieve user interactions or initialize as an empty list
        user_interact = review_obj.user_interaction or []

        # Return early if feedback hasn't changed
        if previous_feedback == study["feedback"]:
            return user_interact

        # Extract study details
        pmid = study["pmid"]
        feedback = study["feedback"]
        timestamp = study["feedback_updated_at"]

        if feedback == "unjudge":
            # Remove entries with the same PMID
            user_interact = [item for item in user_interact if item["pmid"] != pmid]
        else:
            # Attempt to find the study in the list
            for item in user_interact:
                if item["pmid"] == pmid:
                    # Update existing entry
                    item.update({"feedback": feedback, "timestamp": timestamp})
                    break
            else:
                # Append a new entry if not found
                user_interact.append({"pmid": pmid, "feedback": feedback, "timestamp": timestamp})

        return user_interact

    # Validate indices and structure
    if page_index >= len(review_obj.ranking_pages) or page_index < 0:
        raise ValueError(f"Page index {page_index} is out of range.")
    
    ranking_page = review_obj.ranking_pages[page_index]
    
    if "in_page_docs" not in ranking_page or in_page_rank_index >= len(ranking_page["in_page_docs"]) or in_page_rank_index < 0:
        raise ValueError(f"In-page rank index {in_page_rank_index} is out of range or 'in_page_docs' is missing.")
    
    # Access the specific study
    study = ranking_page["in_page_docs"][in_page_rank_index]
    
    # Validate PMID
    if "pmid" not in study or study["pmid"] != pmid:
        raise ValueError(f"Mismatch: Page({page_index}), Rank Index({in_page_rank_index}), PMID({pmid}) not found.")
    
    # Capture previous feedback
    previous_feedback = study.get("feedback", None)
    
    # Update feedback fields
    now = get_utc_datetime()
    study["feedback"] = feedback
    study["feedback_created_at"] = now if study["feedback_created_at"] is None else study["feedback_created_at"]
    study["feedback_updated_at"] = now
    
    # Save changes
    review_obj.ranking_pages[page_index]["in_page_docs"][in_page_rank_index] = study
    review_obj.user_interaction = update_user_interact(previous_feedback, study)
    review_obj.save()
    
    # Return previous feedback
    return previous_feedback


def updated_review_type(review_obj, pmid, previous_feedback, feedback):
    # Helper to update a specific list by removing and adding items
    def update_list(doc_list, pmid, action, title=None):
        if action == "remove":
            doc_list[:] = [doc for doc in doc_list if doc.get("pmid") != pmid]
        elif action == "add" and title is not None:
            doc_list.append({"pmid": pmid, "title": title})
    
    # Initialize lists
    doc_lists = {
        "include": review_obj.include_docs or [],
        "exclude": review_obj.exclude_docs or [],
        "maybe": review_obj.maybe_docs or []
    }

    # Remove item from the previous feedback list, if it exists
    if previous_feedback in doc_lists:
        update_list(doc_lists[previous_feedback], pmid, "remove")

    # Add item to the new feedback list, if applicable
    if feedback in doc_lists:
        title = review_obj.corpus.pmids[pmid].get("title")
        update_list(doc_lists[feedback], pmid, "add", title=title)

    # Update review_obj lists
    review_obj.include_docs = doc_lists["include"]
    review_obj.exclude_docs = doc_lists["exclude"]
    review_obj.maybe_docs = doc_lists["maybe"]

    # Save changes
    review_obj.save()


def count_user_interaction(user_interaction):
    counter = 0
    x_axis, y_axis = [], []
    for i, j in enumerate(user_interaction or []):
        if j["feedback"] == "include":
            counter += 1
        elif j["feedback"] == "unjudge":
            pass

        x_axis.append(i+1)
        y_axis.append(counter)
    
    if len(x_axis) == 0 and len(y_axis) == 0:
        return [0], [0]
    else:
        return x_axis, y_axis

def summary_data(review_obj, page_index, show_total=True):
    # Prepare dashboard data
    dashboard_data = dict()

    # Extract ranking pages and the current page's documents
    ranking_pages = review_obj.ranking_pages
    current_page_docs = ranking_pages[page_index]["in_page_docs"]
    
    # Initialize counters
    feedback_counter = {"include": 0, "exclude": 0, "maybe": 0}

    # Count feedback on the current page
    for doc in current_page_docs:
        feedback = doc.get("feedback", None)
        if feedback in feedback_counter:
            feedback_counter[feedback] += 1

    # Prepare dashboard data
    dashboard_data["current_page_review"] = {
        "total_number_to_review": len(current_page_docs),
        "reviewed": sum(feedback_counter.values()),
        "include": feedback_counter["include"],
        "maybe": feedback_counter["maybe"],
        "exclude": feedback_counter["exclude"]
    }

    # Total counter
    if show_total:
        # Initialize counters
        total_number_to_review = 0
        total_feedback = {"include": 0, "exclude": 0, "maybe": 0}
    
        # Count total documents and feedback across all pages
        # for page in ranking_pages:
        #     total_number_to_review += len(page["in_page_docs"]) + len(page["remaining_ranking"])
        total_number_to_review += len(ranking_pages[0]["in_page_docs"]) + len(ranking_pages[0]["remaining_ranking"])

        # Aggregate totals from include, exclude, maybe
        total_feedback["include"] = len(review_obj.include_docs or [])
        total_feedback["exclude"] = len(review_obj.exclude_docs or [])
        total_feedback["maybe"] = len(review_obj.maybe_docs or [])
        total_reviewed = sum(total_feedback.values())

        # Prepare dashboard data
        dashboard_data["total_page_review"] = {
            "total_number_to_review": total_number_to_review,
            "reviewed": total_reviewed,
            "include": total_feedback["include"],
            "maybe": total_feedback["maybe"],
            "exclude": total_feedback["exclude"]
        }

        # Count user interaction
        x_axis, y_axis = count_user_interaction(review_obj.user_interaction)
        dashboard_data["relevance_discovery_curve"] = {
            "x-axis": {
                "value": x_axis,
                "label": "No. of Reviewed Clinical Studies"
            },
            "y-axis": {
                "value": y_axis,
                "label": "No. of Relevant Clinical Studies"
            }
        }

    return dashboard_data


def validate_prev_review(prev_review):
    # Validate in page of previous review
    for item in prev_review:
        if item["feedback"] == "unjudge":
            return True


def update_page_screening_log(review_obj, page_index, is_done=False):
    # Define variables
    page_screening_log = review_obj.page_screening_log or []  # Default to empty list
    now = get_utc_datetime()  # Get current UTC datetime

    # Ensure the log list has enough entries for the given index
    while len(page_screening_log) <= page_index:  # Expand the list if index doesn't exist
        page_screening_log.append({"started_at": now, "lastest_resumed_at": now, "finished_at": None})

    # Update the log for the given index
    page_screening_log[page_index]["lastest_resumed_at"] = now  # Always update 'lastest_resumed_at'

    # Mark as finished if specified
    if is_done:
        page_screening_log[page_index]["finished_at"] = now

    # Save updated log back to the review object
    review_obj.page_screening_log = page_screening_log
    review_obj.save()


def get_all_pages(review_obj):
    # Extract ranking pages and the current page's documents
    ranking_pages       = review_obj.ranking_pages
    show_docs_per_page  = review_obj.show_docs_per_page

    # Count number to review
    total_number_to_review = len(ranking_pages[0]["in_page_docs"]) + len(ranking_pages[0]["remaining_ranking"])

    # Calculate
    return math.ceil(total_number_to_review / show_docs_per_page)


def summary_review_progress(data: list):
    # Initialize counters
    feedback_counter = {"include": 0, "exclude": 0, "maybe": 0}

    for doc in data:
        feedback = doc.get("feedback", None)
        if feedback in feedback_counter:
            feedback_counter[feedback] += 1
    
    # Prepare dashboard data
    dashboard_data = {
        "reviewed": sum(feedback_counter.values()),
        "include": feedback_counter["include"],
        "maybe": feedback_counter["maybe"],
        "exclude": feedback_counter["exclude"]
    }

    return dashboard_data

def remove_file_from_local_storage(file_path):
    """
    Remove the specified file or the latest file in the specified directory.
        @param      file_path   string   Path to the file or directory.
    """
    if os.path.isdir(file_path):
        # Get the list of files in the directory
        files = os.listdir(file_path)
        if files:
            # Remove the latest file
            latest_file = os.path.join(file_path, files[-1])
            os.remove(latest_file)
            logging.info(f"Removed file: {latest_file}")
        else:
            logging.warning(f"No files to remove in directory: {file_path}")
    else:
        # Remove the file
        os.remove(file_path)
        logging.info(f"Removed file: {file_path}")