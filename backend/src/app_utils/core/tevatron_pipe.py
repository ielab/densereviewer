import pandas as pd
import argparse
import subprocess
from timeit import default_timer as timer
import os

def dpr_pipeline(train_model_path, project_id, query_path, query_encode_dir, corpus_path, corpus_encode_dir, init_rank_dir):
    """
    Get initial ranking with trained dense retriever model
    """

    model_id = train_model_path.split('/')[-1]
    #project_id = 'clef19_intervention'
    corpus_encode_path = f'{corpus_encode_dir}/{project_id}/{model_id}'
    corpus_encode_filename = f'{project_id}_corpus.pkl'

    if not os.path.exists(corpus_encode_path):
        os.makedirs(corpus_encode_path)

        cmd_encode_corpus = f'python -m tevatron.driver.encode \
               --model_name_or_path {train_model_path} \
               --fp16 \
               --per_device_eval_batch_size 256 \
               --p_max_len 128 \
               --dataset_name Tevatron/msmarco-passage-corpus \
               --encode_in_path {corpus_path}  \
               --encoded_save_path {os.path.join(corpus_encode_path, corpus_encode_filename)} \
               --output_dir=temp \
            '
        subprocess.run(cmd_encode_corpus, shell=True, check=True)
    print('Processed corpus encoding with Tevatron.')

    n_docs = len(pd.read_pickle(f'{os.path.join(corpus_encode_path, corpus_encode_filename)}')[1])

    query_encode_path = f'{query_encode_dir}/{project_id}/{model_id}'
    query_encode_filename = f'{project_id}_query_pico.pkl'
    if not os.path.exists(query_encode_path):
        os.makedirs(query_encode_path)

        cmd_encode_query = f'python -m tevatron.driver.encode \
               --model_name_or_path  {train_model_path} \
               --fp16 \
               --p_max_len 128 \
               --dataset_name Tevatron/msmarco-passage/dev \
               --encode_in_path {query_path}  \
               --encode_is_qry \
               --encoded_save_path {os.path.join(query_encode_path, query_encode_filename)} \
               --output_dir=temp \
            '
        subprocess.run(cmd_encode_query, shell=True, check=True)
    print('Processed query encoding with Tevatron.')

    init_rank_path = f'{init_rank_dir}/{project_id}/{model_id}'
    init_rank_filename = f'{project_id}_rank_pico.txt'
    if not os.path.exists(init_rank_path):
        os.makedirs(f'{init_rank_path}')

    # Tevatron retrieval
    cmd_retrieve = f'python -m tevatron.faiss_retriever \
       --query_reps {os.path.join(query_encode_path, query_encode_filename)} \
       --passage_reps {os.path.join(corpus_encode_path, corpus_encode_filename)} \
       --depth {n_docs} \
       --batch_size -1 \
       --save_text \
       --save_ranking_to {os.path.join(init_rank_path, init_rank_filename)} \
    '
    subprocess.run(cmd_retrieve, shell=True, check=True)
    print('Processed initial ranking with Tevatron.')
    return os.path.join(init_rank_path, init_rank_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", default="clef19_intervention", type=str,
                        help="ID of the Systematic Review Project based on the corpus topic")
    # parser.add_argument("--train_model_path", default="./trained_models/clef19_intervention/biolinkbert_128_256_11", type=str,
    #                     help="Path of the trained model")
    parser.add_argument("--train_model_path", default="/home/ubuntu/max/trained_models/clef19_intervention/biolinkbert_128_256_11", type=str,
                        help="Path of the trained model")
    parser.add_argument("--query_path", default="./query.json",
                        type=str,
                        help="Path of the query file")
    parser.add_argument("--query_encode_dir", default="./tevatron_queries_encode/",
                        type=str,
                        help="Directory of the query encoding.")
    # parser.add_argument("--corpus_path", default="./corpus4tevatron.jsonl",
    #                     type=str,
    #                     help="Directory of the corpus file.")
    parser.add_argument("--corpus_path", default="/home/ubuntu/max/corpus4tevatron.jsonl",
                        type=str,
                        help="Directory of the corpus file.")
    parser.add_argument("--corpus_encode_dir", default="./tevatron_corpus_encode/",
                        type=str,
                        help="Directory of the corpus encoding.")
    parser.add_argument("--init_rank_dir", default="./tevatron_results/",
                        type=str,
                        help="Directory of the initial ranking.")

    args = parser.parse_args()

    # start_timer = timer()
    dpr_pipeline(args.train_model_path, args.project_id, args.query_path, args.query_encode_dir, args.corpus_path, args.corpus_encode_dir, args.init_rank_dir)
    # end_timer = timer()
    #print(f'Time used: {end_timer - start_timer} seconds.')