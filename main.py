import argparse
import json
from app.agent import FilumAgent
from app.schema import AgentInput


def main():
    parser = argparse.ArgumentParser(description="Run Filum Pain Point to Solution Agent.")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON file")
    parser.add_argument("--output", type=str, default="output.json", help="Path to output JSON file")
    args = parser.parse_args()

    # Load input
    with open(args.input, "r", encoding="utf-8") as f:
        input_data = json.load(f)
        agent_input = AgentInput(**input_data)

    # Run agent
    agent = FilumAgent()
    output = agent.run(agent_input)

    # Save output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output.json(indent=2))

    print(f"Suggestions written to {args.output}")


if __name__ == "__main__":
    main()
