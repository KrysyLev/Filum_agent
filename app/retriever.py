import json
from typing import List, Dict
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from app.schema import AgentInput


class FeatureRetriever:
    def __init__(self, kb_path: str = "data/feature_kb.json", index_path: str = "data/index"):
        self.kb_path = kb_path
        self.index_path = index_path
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.features = self._load_kb()
        self.index = self._build_or_load_index()

    def _load_kb(self) -> List[Dict]:
        with open(self.kb_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_or_load_index(self):
        index_file = Path(self.index_path) / "faiss.index"
        if index_file.exists():
            index = faiss.read_index(str(index_file))
        else:
            embeddings = self.model.encode(
                [f["description"] + " " + f["how_it_helps"] for f in self.features],
                convert_to_numpy=True
            )
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            Path(self.index_path).mkdir(parents=True, exist_ok=True)
            faiss.write_index(index, str(index_file))
        return index

    def retrieve(self, agent_input: AgentInput, top_k: int = 5) -> List[Dict]:
        query = agent_input.pain_point
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector), top_k)

        # get top-k features by semantic match
        candidates = [self.features[i] for i in indices[0]]

        # hybrid logic: filter or rerank using metadata from company_profile
        return self._rerank_with_context(agent_input, candidates)

    def _rerank_with_context(self, agent_input: AgentInput, candidates: List[Dict]) -> List[Dict]:
        profile = agent_input.company_profile
        for f in candidates:
            score = 1.0

            # industry match
            if profile and profile.industry:
                if profile.industry not in f.get("industries", []):
                    score *= 0.9  # downweight if not matched

            # team size fit
            if profile and profile.team_size:
                if profile.team_size not in f.get("recommended_team_size", []):
                    score *= 0.8

            # touchpoint match
            if profile and profile.customer_touchpoints:
                overlap = set(profile.customer_touchpoints).intersection(set(f.get("channels_supported", [])))
                if not overlap:
                    score *= 0.85

            f["relevance_score"] = round(score, 4)

        # sort by adjusted score (semantic relevance * metadata match)
        return sorted(candidates, key=lambda x: x["relevance_score"], reverse=True)
