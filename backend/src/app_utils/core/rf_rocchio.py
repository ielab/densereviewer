import numpy as np
from typing import List, Dict


class RocchioRf:
    def __init__(self, alpha: float, beta: float, gamma: float, top_k: int):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self._top_k = top_k

    def get_top_k(self):
        return self._top_k

    def set_top_k(self, value):
        if value >= 0:
            self._top_k = value
        else:
            raise ValueError("top_k must be a non-negative value")

    def get_rf_q_emb(self, emb_qs: np.ndarray, rf_candidates: List[Dict]):
        pos_doc_embs, neg_doc_embs = self.get_rf_d_embs(rf_candidates)
        weighted_query_embs = self.alpha * emb_qs

        if len(pos_doc_embs) > 0:
            weighted_mean_pos_doc_embs = self.beta * np.mean(pos_doc_embs, axis=0)
            new_emb_q = weighted_query_embs + weighted_mean_pos_doc_embs
        else:
            new_emb_q = weighted_query_embs

        if len(neg_doc_embs) > 0:
            weighted_mean_neg_doc_embs = self.gamma * np.mean(neg_doc_embs, axis=0)
            new_emb_q -= weighted_mean_neg_doc_embs

        return new_emb_q

    def get_rf_d_embs(self, rf_candidates: List[Dict]):
        pos_doc_embs = []
        neg_doc_embs = []

        for doc in rf_candidates:
            if doc['feedback'] == 'include':
                pos_doc_embs.append(doc['vectors'])
            elif doc['feedback'] == 'exclude':
                neg_doc_embs.append(doc['vectors'])
            # 'maybe' feedback is not used in the Rocchio algorithm

        # if len(pos_doc_embs)==0:
        #     pos_doc_embs = np.zeros(emb_dim)
        # elif len(neg_doc_embs)==0:
        #     neg_doc_embs = np.zeros(emb_dim)

        return np.array(pos_doc_embs), np.array(neg_doc_embs)