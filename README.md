# Filum Agent

Filum Agent is a Python-based solution designed to help businesses address pain points by recommending relevant features from a knowledge base. It uses semantic search and hybrid ranking techniques to match business problems with potential solutions.

## How It Works

1. **Input**: The agent takes a JSON file as input, which describes the business pain point and company profile.
2. **Feature Retrieval**: 
   - The `FeatureRetriever` class loads a feature knowledge base (`data/feature_kb.json`) and builds or loads a FAISS index for efficient vector search.
   - Semantic search is performed using Sentence Transformers to find the most relevant features based on the pain point.
   - Hybrid ranking adjusts the relevance scores based on metadata such as industry, team size, and customer touchpoints.
3. **Output**: The agent generates a list of suggested solutions, including feature names, descriptions, relevance scores, and links, which are saved to an output JSON file.

## File Structure

```
.
├── app/
│   ├── agent.py          # Main agent logic
│   ├── retriever.py      # Feature retrieval and ranking
│   ├── schema.py         # Data models for input and output
├── data/
│   ├── feature_kb.json   # Feature knowledge base
│   ├── index/            # Directory for FAISS index files
├── input.json            # Example input file
├── output.json           # Example output file
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
├── LICENCSE              # LICENCSE

```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KrysyLev/Filum_agent.git Filum_agent
   cd Filum_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-Line Interface

Run the agent using the `main.py` script:

```bash
python main.py --input input.json --output output.json
```

- `--input`: Path to the input JSON file describing the pain point and company profile.
- `--output`: Path to the output JSON file where suggested solutions will be saved.

### Input Format

The input JSON file should follow this structure:

```json
{
    "pain_point": "Our support agents are overwhelmed by the high volume of repetitive questions.",
    "company_profile": {
        "industry": "e-commerce",
        "customer_touchpoints": ["webchat", "email"],
        "team_size": "small",
        "region": "VN"
    },
    "priority": "high"
}
```

### Output Format

The output JSON file will contain suggested solutions:

```json
{
    "suggested_solutions": [
        {
            "feature_name": "AI Agent for FAQ & First Response",
            "categories": ["AI Customer Service", "AI Inbox"],
            "description": "Automatically answers repetitive customer questions using an AI agent.",
            "how_it_helps": "Reduces support volume by handling common queries instantly.",
            "relevance_score": 0.2311,
            "link": "https://filum.ai/features/ai-inbox"
        },
        ...
    ]
}
```
## How It Works Internally

### FeatureRetriever

The `FeatureRetriever` class is responsible for loading the knowledge base, performing semantic search, and reranking results based on business context.

#### `retrieve(self, agent_input: AgentInput, top_k: int = 3) -> List[Dict]`

**Purpose**:  
Retrieves the top `k` most relevant features from the knowledge base using semantic similarity and reranks them based on business context.

**Steps**:  
1. Extract the pain point query:  
    ```python
    query = agent_input.pain_point
    ```
2. Generate embedding vector for the query:  
    ```python
    query_vector = self.model.encode([query])
    ```
3. Search for the top `k` most semantically similar features in the FAISS index:  
    ```python
    distances, indices = self.index.search(np.array(query_vector), top_k)
    ```
    - `distances`: L2 distance between the query and each feature.  
3. Search for the top `k` most semantically similar features in the FAISS index:  
    ```python
    distances, indices = self.index.search(np.array(query_vector), top_k)
    ```
    - `distances`: L2 distance between the query and each feature.  
    - `indices`: Index of each matched feature in the knowledge base.

4. Retrieve the actual feature metadata:  
    ```python
    candidates = [self.features[i] for i in indices[0]]
    ```

5. (Optional) Print debug info on L2 distances:  
    ```python
    print(f"[{i + 1}] {f['feature_name']} - L2 Distance: {dist:.4f}")
    ```

6. Pass to `_rerank_with_context()` for hybrid reranking:  
    ```python
    return self._rerank_with_context(agent_input, candidates, distances)
    ```

---

### `_rerank_with_context(self, agent_input: AgentInput, candidates: List[Dict], distances=None) -> List[Dict]`

**Purpose**:  
This function takes the semantically matched feature list and adjusts their scores based on business context to return a more tailored recommendation.

**Step-by-step**:  
1. Convert FAISS distances into cosine-like similarity:  
    ```python
    similarities = [1 / (1 + d) for d in distances[0]]
    ```
    - Higher values for smaller distances.  
    - Ensures relevance grows as semantic similarity increases.

2. Apply softmax to normalize the scores:  
    ```python
    softmax_scores = np.exp(similarities) / np.sum(np.exp(similarities))
    ```
    - Ensures scores are in range (0, 1).  
    - Makes ranking more distinct and interpretable.

3. Loop through each candidate and apply hybrid context weights:  
    ```python
    if profile.industry not in feature["industries"]: score *= 0.9
    if profile.team_size not in feature["recommended_team_size"]: score *= 0.85
    if no channel overlap: score *= 0.85
    ```

4. Attach final relevance score to each feature:  
    ```python
    f["relevance_score"] = round(float(score), 4)
    ```

5. Return the top features sorted by adjusted relevance:  
    ```python
    return sorted(reranked, key=lambda x: x["relevance_score"], reverse=True)
    ```

### **FilumAgent**:
   - Uses `FeatureRetriever` to retrieve and rank features.
   - Converts raw matches into structured output using Pydantic models.

### **CLI**:
   - Parses input and output file paths.
   - Executes the agent and saves the results.

## Dependencies

- `pydantic>=2.0`
- `sentence-transformers>=2.2.2`
- `faiss-cpu>=1.7.4`

## Example

### Input

```json
{
    "pain_point": "Our support agents are overwhelmed by the high volume of repetitive questions.",
    "company_profile": {
        "industry": "e-commerce",
        "customer_touchpoints": ["webchat", "email"],
        "team_size": "small",
        "region": "VN"
    },
    "priority": "high"
}
```

### Command

```bash
python main.py --input input.json --output output.json
```

### Output

```json
{
    "suggested_solutions": [
        {
            "feature_name": "AI Agent for FAQ & First Response",
            "categories": ["AI Customer Service", "AI Inbox"],
            "description": "Automatically answers repetitive customer questions using an AI agent.",
            "how_it_helps": "Reduces support volume by handling common queries instantly.",
            "relevance_score": 0.2311,
            "link": "https://filum.ai/features/ai-inbox"
        },
        ...
    ]
}
```

## License

This project is licensed under the MIT License.
