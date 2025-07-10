import json
from typing import List, Dict
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from app.schema import AgentInput


class FeatureRetriever:
    """
    FeatureRetriever is a class designed to retrieve relevant features based on semantic similarity
    and contextual metadata. It uses a pre-trained SentenceTransformer model "all-MiniLM-L6-v2" for embedding generation
    and FAISS for efficient similarity search.

    Attributes:
        kb_path (str): Path to the knowledge base JSON file containing feature descriptions.
        index_path (str): Path to store or load the FAISS index.
        model (SentenceTransformer): Pre-trained sentence transformer model for embedding generation.
        features (List[Dict]): List of features loaded from the knowledge base.
        index (faiss.Index): FAISS index for efficient similarity search.

    Methods:
        __init__(kb_path: str, index_path: str):
            Initializes the FeatureRetriever with paths to the knowledge base and FAISS index.

        _load_kb() -> List[Dict]:
            Loads the knowledge base from the specified JSON file.

        _build_or_load_index():
            Builds a FAISS index from feature embeddings or loads an existing index from disk.

        retrieve(agent_input: AgentInput, top_k: int = 5) -> List[Dict]:
            Retrieves the top-k relevant features based on semantic similarity to the agent's input.

        _rerank_with_context(agent_input: AgentInput, candidates: List[Dict], distances=None) -> List[Dict]:
            Reranks the retrieved features using contextual metadata from the agent's company profile.
    """

    def __init__(
        self, kb_path: str = "data/feature_kb.json", index_path: str = "data/index"
    ):
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
                convert_to_numpy=True,
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

        # Print out distance of vector L2
        print("\n[Semantic Search Results - Raw FAISS Distances]")
        for i, (f, dist) in enumerate(zip(candidates, distances[0])):
            print(f"[{i + 1}] {f['feature_name']} - L2 Distance: {dist:.4f}")

        # hybrid logic: filter or rerank using metadata from company_profile
        return self._rerank_with_context(agent_input, candidates, distances)

    def _rerank_with_context(
        self, agent_input: AgentInput, candidates: List[Dict], distances=None
    ) -> List[Dict]:
        profile = agent_input.company_profile

        # Convert FAISS L2 distance to cosine-like similarity (roughly)
        similarities = [1 / (1 + d) for d in distances[0]]  # simple inverse
        similarities = np.array(similarities)
        softmax_scores = np.exp(similarities) / np.sum(np.exp(similarities))

        reranked = []
        for i, f in enumerate(candidates):
            score = softmax_scores[i]

            # Apply hybrid weights
            if profile:
                # Industry match
                if profile.industry and profile.industry not in f.get("industries", []):
                    score *= 0.9

                # Team size fit
                if profile.team_size and profile.team_size not in f.get(
                    "recommended_team_size", []
                ):
                    score *= 0.85

                # Touchpoint overlap
                if profile.customer_touchpoints:
                    overlap = set(profile.customer_touchpoints).intersection(
                        set(f.get("channels_supported", []))
                    )
                    if not overlap:
                        score *= 0.85

            f["relevance_score"] = round(float(score), 4)
            reranked.append(f)

        return sorted(reranked, key=lambda x: x["relevance_score"], reverse=True)
