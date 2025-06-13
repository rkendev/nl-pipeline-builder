import argparse
from nlpipeline.llm_agent import generate_pipeline_spec

def main():
    parser = argparse.ArgumentParser(description="AI Data Pipeline Builder")
    parser.add_argument(
        "description",
        type=str,
        help="Natural language pipeline description"
    )
    args = parser.parse_args()

    # generate_pipeline_spec() already returns pretty-printed JSON
    print(generate_pipeline_spec(args.description))

if __name__ == "__main__":
    main()
