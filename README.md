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
│   ├── utils.py          # Utility functions
├── data/
│   ├── feature_kb.json   # Feature knowledge base
│   ├── index/            # Directory for FAISS index files
├── input.json            # Example input file
├── output.json           # Example output file
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
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

1. **FeatureRetriever**:
   - Loads the knowledge base from `data/feature_kb.json`.
   - Builds or loads a FAISS index for efficient vector-based search.
   - Performs semantic search using Sentence Transformers.
   - Reranks results based on company profile metadata.

2. **FilumAgent**:
   - Uses `FeatureRetriever` to retrieve and rank features.
   - Converts raw matches into structured output using Pydantic models.

3. **CLI**:
   - Parses input and output file paths.
   - Executes the agent and saves the results.

## Dependencies

- `langchain>=0.1.13`
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
```
