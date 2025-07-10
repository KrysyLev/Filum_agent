from app.schema import AgentInput, AgentOutput, SuggestedSolution
from app.retriever import FeatureRetriever

class FilumAgent:
    """
    Module: agent

    This module defines the `FilumAgent` class, which serves as the main agent for processing user input
    and generating suggested solutions based on retrieved features.

    Classes:
        FilumAgent:
            A class that encapsulates the logic for retrieving relevant features and converting them
            into suggested solutions.

            Methods:
                __init__():
                    Initializes the FilumAgent instance and sets up the FeatureRetriever.

                run(user_input: AgentInput) -> AgentOutput:
                    Processes the user input, retrieves relevant features, and generates a list of
                    suggested solutions encapsulated in an AgentOutput object.

    Usage:
        Instantiate the `FilumAgent` class and call the `run` method with an `AgentInput` object to
        retrieve suggested solutions based on the input.
    """
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
