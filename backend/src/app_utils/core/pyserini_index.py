import os
import glob
import argparse
import subprocess
from timeit import default_timer as timer
from tqdm import tqdm


# def index_corpus(corpus_path:str, model_path:str):
#     model_name = model_path.split('/')[-1]
#     corpus_name = 'clef19_intervention' #corpus_path
#     embedding_path = f'indexes/encoding/{model_name}/{corpus_name}'
#     if not os.path.exists(embedding_path):
#         os.makedirs(embedding_path)
#     index_path = f'indexes/{model_name}/{corpus_name}'
#     if not os.path.exists(index_path):
#         os.makedirs(index_path)

#     cmd_encode = f'python -m pyserini.encode \
#             input --corpus {corpus_path} \
#             --fields text \
#             --delimiter "\n" \
#             --shard-id 0 \
#             --shard-num 1 \
#             output --embeddings {embedding_path}/ \
#             --to-faiss \
#             encoder --encoder {model_path} \
#             --fields text \
#             --batch 32 \
#             --fp16 \
#             '
#     subprocess.run(cmd_encode, shell=True, check=True)

#     cmd_index = f'python -m pyserini.index.faiss \
#                 --input indexes/encoding/{model_name}/{corpus_name}/ \
#                 --output {index_path}/ \
#                 '
#     subprocess.run(cmd_index, shell=True, check=True)

#     print(f'Encoding {corpus_name} Finished')


def index_corpus(corpus_path:str, model_path:str, **kwargs):
    """
    Film: I've added `dynamic_save_path` and `corpus_name` to the function, which retrieve values from **kwargs. This allows the function to save the indexing file to a user-specified location.

    Key                     Type        Description
    dynamic_save_path       string      The path to the user's directory (e.g., /app/backend/src/user-corpus/u00002/corpus/c00044).
                                        If the function cannot retrieve the `dynamic_save_path` key from **kwargs, 
                                        it will use the default value (/home/ubuntu/max).

    corpus_name             string      Represents the corpus name or identifier. By default, this is set to 'clef19_intervention'. 
                                        In the backend API context, this key corresponds to the `review_id` (e.g., r00005).
    """

    # Get other keyword arguments
    dynamic_save_path = kwargs.get("dynamic_save_path", "/home/ubuntu/max")
    corpus_name = kwargs.get("review_id", "clef19_intervention")

    model_name = model_path.split('/')[-1]
    # corpus_name = 'clef19_intervention' #corpus_path
    embedding_path = f'indexes/encoding/{model_name}/{corpus_name}'

    # Concat dynamic_save_path and embedding_path
    embedding_path = os.path.join(dynamic_save_path, embedding_path)
    if not os.path.exists(embedding_path):
        os.makedirs(embedding_path)

    # Concat dynamic_save_path and index_path
    index_path = f'indexes/{model_name}/{corpus_name}'
    index_path = os.path.join(dynamic_save_path, index_path)
    if not os.path.exists(index_path):
        os.makedirs(index_path)

    cmd_encode = f'python -m pyserini.encode \
            input --corpus {corpus_path} \
            --fields text \
            --delimiter "\n" \
            --shard-id 0 \
            --shard-num 1 \
            output --embeddings {embedding_path}/ \
            --to-faiss \
            encoder --encoder {model_path} \
            --fields text \
            --batch 32 \
            --fp16 \
            '
    subprocess.run(cmd_encode, shell=True, check=True)

    cmd_index = f'python -m pyserini.index.faiss \
                --input {embedding_path} \
                --output {index_path}/ \
                '
    subprocess.run(cmd_index, shell=True, check=True)

    print(f'Encoding {corpus_name} Finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus_path", default="clef", type=str)
    parser.add_argument("--model_path", default="bert-base-uncased", type=str, help="huggingface encoders")
    args = parser.parse_args()

    start_timer = timer()
    index_corpus(args.corpus_path, args.model_path)
    end_timer = timer()
    print(end_timer - start_timer)
    print('Indexing Finished')