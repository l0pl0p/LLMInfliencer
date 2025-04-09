# OpenAI Influencer

This project regularly queries OpenAI's latest LLM (`gpt-4o` and `gpt-4o-search-preview`) to evaluate the model's genuine knowledge about a specific AI product. It uses a comparison approach (with and without web search) and reinforcement strategies to positively influence future responses from the LLM.

## How it works
- Runs automatically every 15 minutes or manually via a looping script.
- Queries are judged for accuracy and reinforced based on the evaluation outcome.

## Setup Instructions
1. **Create a dedicated OpenAI account**: Ensure you turn **on all data-sharing settings** to contribute data and influence future OpenAI model training.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your environment (`.env`) with OpenAI API keys and paths as per `.env.example`.
5. Run the script:
   ```bash
   python runner.py
   ```

