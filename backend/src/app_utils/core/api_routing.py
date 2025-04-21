import nbib
import json
import pandas as pd

"""
1. Function/API route
parse the nbib file and store in the database
"""
def parse_corpus(corpus_nbib_path: str, corpus_file: str = 'corpus.json') -> json:
    """
    Parse a corpus from a nbib file and extract specific fields into a JSON format.

    Args:
        corpus_nbib_path (str): Path to the corpus text in nbib format.
        corpus_file (str): Output file path for the resulting JSON file (default is 'corpus.json').
    """
    output_name = corpus_file
    keep_fields = ['pubmed_id', 'title', 'abstract', 'authors']
    refs = nbib.read_file(corpus_nbib_path)

    # first_entry = refs[0]
    filtered_entries = []

    for study in refs:
        filtered = {field: study.get(field, "") for field in keep_fields}

        if 'pubmed_id' in filtered:
            filtered['pmid'] = filtered.pop('pubmed_id')

        filtered_entries.append(filtered)

    with open(output_name, 'w') as f:
        json.dump(filtered_entries, f, indent=4)

def preview_corpus(corpus_nbib_path: str, n_entries: int):
    """
    Extract the first N entries from the corpus nbib file for preview.

    Returns:
        entries: list of first N entries.
    """
    current_entry = []
    entries = []
    with open(corpus_nbib_path, 'r') as infile:
        for line in infile:
            current_entry.append(line)

            if line.strip() == "":
                entries.append("".join(current_entry))
                current_entry = []

                if len(entries) > n_entries:
                    break
    print(entries[n_entries])

    return entries



# def parse_query(pico_path: str, output_path='query.json'):
#     """
#     Assume PICOs are inputted as a dict from a single jsonl, concatenate into a single query for the dense retriever.

#     Args:
#         pico_path (str): Path to the corpus file in nbib format.
#         output_path (str): Output file path for the resulting JSONL file (default is 'query.jsonl').

#     Example Inputs:
#     pico_data = {
#          "P": ["Aged 19 and over", "Extraction Of Catatract"],
#          "I": ["Insertion Of Intraocular Lens"],
#          "C": ["Insertion Of Intraocular Lens"],
#          "O":["Finding Of Color Vision", "Visual Acuity Testing"]
#     }
#     """
#     with open(pico_path, 'r') as infile, open(output_path, 'w') as outfile:
#         for line in infile:
#             pico_data = json.loads(line)
#             p_contact = " ".join(pico_data.get("P", []))
#             i_contact = " ".join(pico_data.get("I", []))
#             c_contact = " ".join(pico_data.get("C", []))
#             o_contact = " ".join(pico_data.get("O", []))

#             # handle when I and C are the same, keep I as the key factor
#             if i_contact == c_contact:
#                 query = f"{p_contact} {i_contact} {o_contact}"
#             else:
#                 query = f"{p_contact} {i_contact} {c_contact} {o_contact}"

#             output_query = {"query_id": "DR000000",
#                             "query": query.strip()}
#             outfile.write(json.dumps(output_query) + '\n')

# parse_query edit version
def parse_query(pico_data: dict, output_path='query.json'):
    """
    Assume PICOs are inputted as a dict, concatenate into a single query for the dense retriever and return output_query as a dictionary.

    Args:
        pico_data (dict): PICO dict

    Example Inputs:
    pico_data = {
         "P": ["Aged 19 and over", "Extraction Of Catatract"],
         "I": ["Insertion Of Intraocular Lens"],
         "C": ["Insertion Of Intraocular Lens"],
         "O": ["Finding Of Color Vision", "Visual Acuity Testing"]
    }
    """
    p_contact = " ".join(pico_data.get("P", []))
    i_contact = " ".join(pico_data.get("I", []))
    c_contact = " ".join(pico_data.get("C", []))
    o_contact = " ".join(pico_data.get("O", []))

    # handle when I and C are the same, keep I as the key factor
    if i_contact == c_contact:
        query = f"{p_contact} {i_contact} {o_contact}"
    else:
        query = f"{p_contact} {i_contact} {c_contact} {o_contact}"

    output_query = {"query_id": "DR000000",
                    "query": query.strip()}
    
    with open(output_path, "w") as outfile:
        json.dump(output_query, outfile)

# def convert_jsonl(input_file: str, output_file: str):
#     """
#     Converts DB JSONL file with 'pubmed_id', 'title', 'abstract', 'authors'
#     to Tevatron JSONL file with 'docid', 'title', and 'abstract'.
#
#     Args:
#     - input_file (str): Path to the input JSONL file.
#     - output_file (str): Path to the output JSONL file.
#     """
#     with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
#         for line in infile:
#             record = json.loads(line)
#
#             new_record = {
#                 'docid': record.get('pubmed_id'),
#                 'title': record.get('title'),
#                 'text': record.get('abstract')
#             }
#
#             outfile.write(json.dumps(new_record) + '\n')


def corpus_converter(corpus_path: str):
    """
    Parse the corpus and output three dicts and saved in json or jsonl files.

    Example Inputs:
    docid2pmid.json = {docid(int): pmid(str),}
    corpus4tevatron.jsonl = {"docid": ,"title": ,"text": }{}
    pmids.json = {"pmid": {"title":,"abstract":,"authors":,}{}}
    """
    docid2pmid = {}
    corpus4tevatron = []
    pmids = {}

    with open(corpus_path, 'r') as infile:
        corpus_data = json.load(infile)

        for study in corpus_data:
            pmid = study.get('pmid')
            title = study.get('title')
            abstract = study.get('abstract')
            authors = study.get('authors')

            docid2pmid[pmid] = str(pmid)

            corpus4tevatron_study = {
                "docid": int(pmid),
                "title": title,
                "text": abstract,
            }
            corpus4tevatron.append(corpus4tevatron_study)

            pmids[str(pmid)] = {
                "title": title,
                "abstract": abstract,
                "authors": authors
            }

        # Edit by Film: there is no need to store it as files because the returned results will be saved to the database
        # with open('docid2pmid.json', 'w') as outfile:
        #     json.dump(docid2pmid, outfile, indent=4)
        # with open('corpus4tevatron.jsonl', 'w') as outfile:
        #     for study in corpus4tevatron:
        #         jsonl_string = json.dumps(study)
        #         outfile.write(jsonl_string + '\n')
        # with open('pmids.json', 'w') as outfile:
        #     json.dump(pmids, outfile, indent=4)

    return docid2pmid, corpus4tevatron, pmids



"""
2. Function/API route
get data from UI and save it to ranking_pages and read data from this variable to perform re-ranking based on Rocchio
"""

def create_ranking_page_template(type: str):
    return {
        "type": type, # "init_ranking" or "dense_rocchio"
        "ranking_at": "",  # Placeholder for time
        "in_page_docs": [],  # Documents that will be shown to the user
        "remaining_ranking": []  # Remaining documents not shown initially
    }

def create_in_page_document_template(rank, pmid, score):
    return {
        "rank": rank,  # Position of the document in ranking
        "pmid": pmid,  # PubMed ID or document ID
        "score": score,  # Document score
        "feedback": "unjudge",  # Feedback value: "unjudge", "include", "maybe", "exclude"
        "feedback_created_at": None,  # Placeholder for feedback creation time (ISO 8601)
        "feedback_updated_at": None  # Placeholder for feedback update time (ISO 8601)
    }

def create_remaining_ranking_document_template(rank, pmid, score):
    return {
        "rank": rank,  # Position of the document in ranking
        "pmid": pmid,  # PubMed ID or document ID
        "score": score,  # Document score
    }

def get_init_ranking(init_rank_path: str, ranking_page_path: str, show_docs=25):
    """
    Read from the saved initial ranking txt from tevatron

    Args:
        ranking_page_path (str): Path to the ranking pages file in .jsonl format.
        init_rank_path (str): Path to the initial ranking file in .txt format.
        show_docs (int): Top n (default 25) from the initial ranking to show to users for feedback.

    """
    ranking_page = []
    type = "init_ranking"
    doc_rank = 1 # To track the rank of each document
    page_template = create_ranking_page_template(type)

    with open(init_rank_path, 'r') as infile:
        for line in infile:
            _, docid, score = line.strip().split('\t')

            # Add to in_page_docs or remaining_ranking based on the show_limit
            if len(page_template["in_page_docs"]) < show_docs:
                # Handle in page docs
                doc_template = create_in_page_document_template(rank=doc_rank, pmid=docid, score=float(score))
                page_template["in_page_docs"].append(doc_template)
            else:
                # Handle remaining docs
                doc_template = create_remaining_ranking_document_template(rank=doc_rank, pmid=docid, score=float(score))
                page_template["remaining_ranking"].append(doc_template)

            doc_rank += 1

        if page_template is not None:
            ranking_page.append(page_template)

        
        # # Write the output JSON
        # with open(ranking_page_path, 'w') as outfile:
        #     json.dump(ranking_page, outfile, indent=4)
            # for page in ranking_page:
            #     outfile.write(json.dumps(page) + '\n')

    # Edit by Film: Because it needs to be saved into the database
    return ranking_page

"""
3. Function/API route
read ranking_pages, extract 3 lists and save to 3 fields in the database, i.e., Include docs, Exclude docs and
Maybe docs. This is to let a user to see in 3 tables according to Include, Exclude and not_sure.
"""
def pmid_to_title_mapping(corpus_path) -> dict:
    """
    Load the corpus.json and create a mapping from pmid to title.
    """
    pmid_to_title = {}

    with open(corpus_path, 'r') as infile:
        records = json.load(infile)
        for record in records:
            pmid = record.get('pmid')
            title = record.get('title')

            if pmid and title:
                pmid_to_title[str(pmid)] = title

    return pmid_to_title

def categorize_document(corpus_path, doc, relevance: str, include: list, exclude: list, maybe: list):
    """
    Categorize a document into include, exclude, or maybe lists based on its feedback.
    """
    pmid_title_dict = pmid_to_title_mapping(corpus_path)
    doc_info = {
        "rank": doc["rank"],
        "pmid": doc["pmid"],
        'title': pmid_title_dict[doc["pmid"]],
        "relevance": relevance  # Extract the relevance from the feedback
    }
    if relevance == "include":
        include.append(doc_info)
    elif relevance == "exclude":
        exclude.append(doc_info)
    elif relevance == "maybe":
        maybe.append(doc_info)


def categorize_documents_by_judgment(ranking_page_path):
    include_list = []
    exclude_list = []
    maybe_list = []

    with open(ranking_page_path, 'r') as infile:
        # Parse the JSON line
        ranking_pages = json.load(infile)

        for ranking_page in ranking_pages:

            # Process in_page_docs
            for doc in ranking_page.get("in_page_docs", []):
                relevance = doc["feedback"]
                categorize_document('corpus.json', doc, relevance, include_list, exclude_list, maybe_list)

            # No need to process remaining_ranking
            # for doc in ranking_page.get("remaining_ranking", []):
            #     relevance = doc["feedback"]["relevance"]
            #     categorize_document('corpus.json', doc, relevance, include_list, exclude_list, maybe_list)

    return include_list, exclude_list, maybe_list


def create_dataframe(include_list, exclude_list, maybe_list):
    """
    Create a big table (Pandas DataFrame) with a column indicating inclusion category.
    """
    # Convert lists to dataframes with a 'judgment' column
    df_include = pd.DataFrame(include_list)

    df_exclude = pd.DataFrame(exclude_list)

    df_maybe = pd.DataFrame(maybe_list)

    # Concatenate all dataframes
    combined_df = pd.concat([df_include, df_exclude, df_maybe], ignore_index=True)

    return combined_df


"""
4. Function/API route
read ranking_pages and output to nbib format
"""
def extract_ranking_info(ranking_pages_path, pmid_to_title):
    """
    Extract rank, pmid, and judgment from ranking_pages.jsonl and look up titles from pmid_to_title mapping.
    """
    data = []

    with open(ranking_pages_path, 'r') as infile:
        ranking_pages = json.load(infile)
        for ranking_page in ranking_pages:
            # Extract from in_page_docs
            for doc in ranking_page.get("in_page_docs", []):
                pmid = doc["pmid"]
                rank = doc["rank"]
                judgment = doc["feedback"]
                title = pmid_to_title.get(pmid, "Title Not Found")  # Lookup title

                data.append({"rank": rank, "pmid": pmid, "title": title, "judgment": judgment})

            #  Skip extracting from remaining_ranking
            # for doc in ranking_page.get("remaining_ranking", []):
            #     pmid = doc["pmid"]
            #     rank = doc["rank"]
            #     # judgment = doc["feedback"]["relevance"]
            #     title = pmid_to_title.get(pmid, "Title Not Found")  # Lookup title
            #
            #     data.append({"rank": rank, "pmid": pmid, "title": title, "judgment": judgment})

    return data


def filter_and_export(df, judgment_type, output_file):
    """
    Filter the DataFrame by judgment type and exports it to CSV.
    """
    filtered_df = df[df['judgment'] == judgment_type]
    filtered_df.to_csv(output_file, index=False)
    print(f"Exported {judgment_type} to {output_file}")


def load_pmids_by_judgment(docs, judgment_type):
    """
    Extract PMIDs from ranking_pages.jsonl based on the provided judgment type.
    """
    # return [doc['pmid'] for doc in docs if doc['relevance'] == judgment_type]
    return [doc['pmid'] for doc in docs if doc['feedback'] in judgment_type]


def extract_nbib_records(corpus_nbib_path, pmids_to_export, output_file):
    """
    Extracts NBIB records from the original corpus based on the provided PMIDs.
    """
    export_records = []
    current_record = []
    record_pmid = None

    with open(corpus_nbib_path, 'r') as infile:
        for line in infile:
            # Check if the line contains a PMID entry
            if line.startswith("PMID- "):
                record_pmid = line.strip().split("PMID- ")[1]

            # Accumulate the current NBIB entry
            current_record.append(line)

            # Check if we've reached the end of the current NBIB record (NBIB records are separated by two newlines)
            if line.strip() == "":
                if record_pmid in pmids_to_export:
                    # If the current record's PMID matches one in our export list, store it
                    export_records.append("".join(current_record))

                # Reset for the next record
                current_record = []
                record_pmid = None

    # Write the extracted records to the output file
    with open(output_file, 'w') as outfile:
        for record in export_records:
            outfile.write(record)
            outfile.write("\n\n")  # Separate NBIB entries with two newlines


def export_by_judgment(docs, judgment_type, input_ris_file, output_nbib_file):
    """
    Function to extract NBIB records based on the judgment type (e.g., 'include', 'exclude', 'maybe').
    """
    # Step 1: Load PMIDs based on the judgment type
    pmids_to_export = load_pmids_by_judgment(docs, judgment_type)
    print(pmids_to_export)

    # Step 2: Extract and export NBIB records based on the selected PMIDs
    extract_nbib_records(input_ris_file, pmids_to_export, output_nbib_file)