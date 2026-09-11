from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def main() -> None:
    policies_dir = Path(__file__).parent / "Policies"
    print("Project initialized successfully.")
    if policies_dir.exists():
        policy_files = list(policies_dir.glob("*.pdf"))
        print(f"Found {len(policy_files)} policy documents in {policies_dir.name}/")


if __name__ == "__main__":
    main()
