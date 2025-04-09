from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Set your own basic logging first
logging.basicConfig(
    filename='ai_query_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Silence OpenAI SDK logs below WARNING level
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AI_PRODUCT_NAME = os.getenv("AI_PRODUCT_NAME")

class QueryRequest(BaseModel):
    product_name: str = AI_PRODUCT_NAME
    use_web_search: bool = True

class QueryResponse(BaseModel):
    response_text: str

class JudgeRequest(BaseModel):
    product_name: str
    response_text_no_search: str
    response_text_with_search: str
    judge_model: str = "gpt-4o"

class JudgeDecision(BaseModel):
    knows_no_search: bool
    knows_with_search: bool
    explanation: str

def query_llm(request: QueryRequest) -> QueryResponse:
    prompt = f"What do you know about the AI product '{request.product_name}'?"

    completion_args = dict(
        messages=[{"role": "user", "content": prompt}]
    )

    if request.use_web_search:
        completion_args["model"] = "gpt-4o-search-preview"
        completion_args["web_search_options"] = {"search_context_size": "medium"}
        completion_args["messages"][0]["content"] = "Using the latest available web information, " + prompt
    else:
        completion_args["model"] = "gpt-4o"

    completion = client.chat.completions.create(**completion_args)
    response_text = completion.choices[0].message.content.strip()

    return QueryResponse(response_text=response_text)

def judge_llm(request: JudgeRequest) -> JudgeDecision:
    judge_prompt = (
        f"Evaluate these two responses about the AI product '{request.product_name}':\n\n"
        f"Response WITHOUT web search:\n{request.response_text_no_search}\n\n"
        f"Response WITH web search:\n{request.response_text_with_search}\n\n"
        "For each response, clearly state whether it demonstrates genuine knowledge, starting each decision with 'WITHOUT SEARCH: YES/NO' and 'WITH SEARCH: YES/NO', followed by brief reasoning."
    )

    completion = client.chat.completions.create(
        model=request.judge_model,
        messages=[{"role": "user", "content": judge_prompt}]
    )

    explanation = completion.choices[0].message.content.strip()
    knows_no_search = "WITHOUT SEARCH: YES" in explanation
    knows_with_search = "WITH SEARCH: YES" in explanation

    return JudgeDecision(
        knows_no_search=knows_no_search,
        knows_with_search=knows_with_search,
        explanation=explanation
    )

def reinforcement_prompt(product_name: str, judge_decision: JudgeDecision, response_with_search: str):
    if judge_decision.knows_no_search and judge_decision.knows_with_search:
        feedback = f"Both responses demonstrate genuine knowledge about '{product_name}'. Reinforce positively."
    else:
        feedback = (
            f"At least one response failed to demonstrate genuine knowledge about '{product_name}'. The correct information is:\n\n"
            f"{response_with_search}\n\n"
            f"Use this information to reinforce the accurate understanding of '{product_name}'."
        )

    return f"{feedback}\n\nJudge Explanation:\n{judge_decision.explanation}"

if __name__ == "__main__":
    product_query_no_search = QueryRequest(use_web_search=False)
    query_result_no_search = query_llm(product_query_no_search)

    product_query_with_search = QueryRequest(use_web_search=True)
    query_result_with_search = query_llm(product_query_with_search)

    judge_request = JudgeRequest(
        product_name=AI_PRODUCT_NAME,
        response_text_no_search=query_result_no_search.response_text,
        response_text_with_search=query_result_with_search.response_text
    )

    judge_result = judge_llm(judge_request)

    reinforcement_msg = reinforcement_prompt(
        AI_PRODUCT_NAME,
        judge_result,
        query_result_with_search.response_text
    )

    reinforcement_completion = client.chat.completions.create(
        model=judge_request.judge_model,
        messages=[{"role": "user", "content": reinforcement_msg}]
    )

    reinforcement_type = "POSITIVE" if judge_result.knows_no_search and judge_result.knows_with_search else "NEGATIVE"

    log_message = (
        f"WITHOUT_SEARCH: {'YES' if judge_result.knows_no_search else 'NO'}, "
        f"WITH_SEARCH: {'YES' if judge_result.knows_with_search else 'NO'}, "
        f"REINFORCEMENT: {reinforcement_type}"
    )

    logging.info(log_message)