from app.schema import AgentInput, AgentOutput, SuggestedSolution
from app.retriever import FeatureRetriever


class FilumAgent:
    def __init__(self):
        self.retriever = FeatureRetriever()

    def run(self, user_input: AgentInput) -> AgentOutput:
        raw_matches = self.retriever.retrieve(user_input)

        solutions = []
        for feature in raw_matches:
            solution = SuggestedSolution(
                feature_name=feature["feature_name"],
                categories=feature.get("categories", []),
                description=feature["description"],
                how_it_helps=feature["how_it_helps"],
                relevance_score=feature.get("relevance_score", 0.0),
                link=feature.get("link")
            )
            solutions.append(solution)

        return AgentOutput(suggested_solutions=solutions)
