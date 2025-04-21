import numpy as np
import pandas as pd
import json
from typing import List, Dict
from pyserini.search import FaissSearcher
# from rf_rocchio import RocchioRf
from app_utils.core.rf_rocchio import RocchioRf      # for importing module under container mounting
from faiss import read_index


class InteractiveRanker:
    def __init__(self, model_path: str, index_path: str, query_embedding_path: str,
                 rocchio_params: List[float] = [1.0, 1.0, 1.0]):
        self.model_path = model_path

        if len(rocchio_params) != 3:
            raise ValueError("rocchio_params must be a list of 3 float values [alpha, beta, gamma]")

        self.alpha, self.beta, self.gamma = rocchio_params

        self.searcher = FaissSearcher(index_path, model_path)

        self.index = read_index(f"{index_path}/index")

        # Load query embedding
        self.query_embedding = pd.read_pickle(query_embedding_path)[0]
        if len(self.query_embedding.shape) == 1:
            self.query_embedding = self.query_embedding.reshape((1, len(self.query_embedding)))

    def generate_ranking_pages(self, feedback_data: Dict, feedback_size: int = 25) -> Dict:
        """
        Read feedback from previous ranking page, and generate new ranking page for the next iteration.

        Args:
            feedback_data (Dict): Studies with feedback from previous page.
            feedback_size (int, optional): Number of studies on each page. Defaults to 25.
        """
        # Process feedback for Rocchio
        rocchio_feedback = []
        doc_idx_list = self.searcher.docids

        for doc in feedback_data['in_page_docs']:
            doc_idx = doc_idx_list.index(doc['pmid'])
            doc_vector = self.index.reconstruct(doc_idx)
            rocchio_feedback.append({
                'docid': doc['pmid'],
                'score': doc['score'],
                'vectors': doc_vector,
                'feedback': doc['feedback']  # Now directly using 'include', 'exclude', or 'maybe'
            })

        # Perform relevance feedback
        rocchio_rf = RocchioRf(alpha=self.alpha, beta=self.beta, gamma=self.gamma,
                               top_k=len(feedback_data['in_page_docs']))

        new_query_embedding = rocchio_rf.get_rf_q_emb(self.query_embedding, rf_candidates=rocchio_feedback)

        if len(new_query_embedding.shape) == 1:
            new_query_embedding = new_query_embedding.reshape((1, len(new_query_embedding)))

        self.query_embedding = new_query_embedding

        # Get the list of PMIDs from remaining_ranking
        remaining_pmids = [doc['pmid'] for doc in feedback_data['remaining_ranking']]

        # Rerank the remaining documents
        reranked_docs = []
        for pmid in remaining_pmids:
            doc_idx = doc_idx_list.index(pmid)
            doc_vector = self.index.reconstruct(doc_idx)
            score = np.dot(self.query_embedding, doc_vector)[0]
            reranked_docs.append((pmid, score))

        # Sort the reranked documents by score
        reranked_docs.sort(key=lambda x: x[1], reverse=True)

        # Prepare new ranking
        in_page_docs = []
        remaining_ranking = []

        for rank, (pmid, score) in enumerate(reranked_docs, start=1):
            if rank <= feedback_size:
                doc_info = {
                    "rank": rank,
                    "pmid": pmid,
                    "score": float(score),
                    "feedback": "unjudge",
                    "feedback_created_at": None,  # Placeholder for feedback creation time (ISO 8601)
                    "feedback_updated_at": None  # Placeholder for feedback update time (ISO 8601)
                }
                in_page_docs.append(doc_info)
            else:
                doc_info = {
                    "rank": rank,
                    "pmid": pmid,
                    "score": float(score),
                }
                remaining_ranking.append(doc_info)

        return {
            "type": "dense_rocchio",
            "in_page_docs": in_page_docs,
            "remaining_ranking": remaining_ranking
        }


# Example usage
if __name__ == "__main__":
    ranker = InteractiveRanker(
        model_path="trained_models/clef19_intervention/biolinkbert_128_256_11",
        index_path="indexes/clef19_intervention/",
        query_embedding_path="tevatron_queries_encode/clef19_intervention/biolinkbert_128_256_11/clef19_intervention_query_pico.pkl",
        rocchio_params=[1.0, 1.0, 1.0]  # [alpha, beta, gamma]
    )

    # Example with initial ranking or the compelted first page
    previous_ranking_page = json.load(open('ranking_pages_feedback.json'))

    new_ranking = ranker.generate_ranking_pages(previous_ranking_page[0])
    print(new_ranking)