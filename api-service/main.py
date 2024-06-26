from dotenv import load_dotenv

load_dotenv()
import json
import openai
import os
import random
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO, BytesIO
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Dict, Tuple
from domain.prompts import TOPIC_SENTENCE_SYSTEM_PROMPT, QUOTATION_SYSTEM_PROMPT
from domain.models import (
    InputData,
    SentenceRankingInput,
    InputDataList,
    RuleInputData,
    UpdateRuleInput,
    CreateRuleInput,
    NgramInput,
)
from utils.adhoc_rule_search import ngram_helper_suggestion, ngram_helper_rule
from utils.utils import (
    generate_simple_message,
    call_gpt_with_backoff,
    setup_logger,
    rank_sentence,
    call_gpt3,
    rewrite_parentheses_helper,
    rewrite_rule_helper,
    pull_xml_from_github,
    update_rule_helper,
    create_rule_helper,
    fetch_rule_by_id,
    create_df_from_analysis_data,
    combine_all_usages,
    check_rule_modification,
)
from utils.rule_splitting import (
    split_rule_by_or_operands,
    split_broad_rule_with_instructions,
)


logger = setup_logger(__name__)


openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/topic-sentence")
def topic_sentence(input_data: InputData):
    """
    Evaluate if the topic sentence needs to be revised, return the revised version if needed
    """
    try:
        messages = generate_simple_message(
            system_prompt=TOPIC_SENTENCE_SYSTEM_PROMPT,
            user_prompt=input_data.input_text,
        )
        response, usage = call_gpt_with_backoff(
            messages=messages, model="gpt-4", temperature=0
        )
        logger.info(f"response from topic sentence analysis: {response}")
        json_response = json.loads(response)
        if (
            json_response["revised_topic_sentence"].lower().replace(".", "")
            == "no changes"
        ):
            logger.info(
                "original sentence didn't need changes, replacing value in output..."
            )
            json_response["revised_topic_sentence"] = input_data.input_text
        json_response["usage"] = usage
        return JSONResponse(content=json_response)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/quotations")
def quotations(input_data: InputData):
    """
    Evaluate if the passage has quotations introduced with fluffy lean-ins and replace them with substantive ones
    """
    try:
        messages = generate_simple_message(
            system_prompt=QUOTATION_SYSTEM_PROMPT, user_prompt=input_data.input_text
        )
        response, usage = call_gpt_with_backoff(messages=messages, temperature=1)
        return JSONResponse(content={"response": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/sentence-ranking")
def sentence_ranking(input_data: SentenceRankingInput):
    """
    Rank the sentence corrections
    """
    try:
        responses = [
            rank_sentence(
                sentence_number=record.sentence_number,
                rule_number=record.rule_number,
                text=record.text,
                corrected_text=record.corrected_text,
            )
            for record in input_data.input_data
        ]
        usages = [response.pop("usage") for response in responses]
        total_usage = defaultdict(float)
        for usage in usages:
            for key, value in usage.items():
                total_usage[key] += value
        return JSONResponse(content={"response": responses, "usage": total_usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/parentheses-rewriting")
def parentheses_rewriting(input_data: InputDataList):
    """
    Rewrite text that has parentheses in it based on criteria
    """
    try:
        response, usage = rewrite_parentheses_helper(input_data=input_data.input_texts)
        return JSONResponse(content={"response": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/generate-next-word")
def generate_next_word(input_sentence: InputData) -> JSONResponse:
    """
    Generate the next possible words with the log probabilities.
    """
    try:
        prompt = f"Generate the most likely word to complete this sentence:\n\n{input_sentence.input_text.strip()}"
        response, usage = call_gpt3(prompt=prompt, temperature=0)
        return JSONResponse(content={"likely_words": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/bulk-generate-next-word")
async def bulk_generate_next_word(file: UploadFile = File(...)) -> JSONResponse:
    """
    Generates the next possible words with the log probabilities for a bulk dataset
    """
    try:
        contents = await file.read()
        # Split the file contents into lines and then into tuples
        lines = [line for line in contents.decode("utf-8").split("\n") if line.strip()]
        response_data = []
        for line in lines:
            response, usage = call_gpt3(prompt=line.strip(), temperature=0)
            response_data.append(
                {"input": line, "likely_words": response, "usage": usage}
            )
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/generate-prev-word")
def generate_prev_word(input_data: InputData) -> JSONResponse:
    """
    Generate the most likely previous word with the log probabilities
    """
    try:
        prompt = f"Fill in the blank in the sentence below:\n\n____ {input_data.input_text.strip()}\n\n"
        response, usage = call_gpt3(prompt=prompt, temperature=0, max_tokens=10)
        return JSONResponse(content={"likely_words": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/bulk-generate-prev-word")
async def bulk_generate_prev_word(file: UploadFile = File(...)) -> JSONResponse:
    """
    Generates the previous possible words with the log probabilities for a bulk dataset
    """
    try:
        contents = await file.read()
        # Split the file contents into lines and then into tuples
        lines = [line for line in contents.decode("utf-8").split("\n") if line.strip()]
        response_data = []
        for line in lines:
            prompt = (
                f"Fill in the blank in the sentence below:\n\n____ {line.strip()}\n\n"
            )
            response, usage = call_gpt3(prompt=prompt, temperature=0, max_tokens=10)
            response_data.append(
                {"input": line, "likely_words": response, "usage": usage}
            )
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/list-rules")
async def list_rules() -> JSONResponse:
    try:
        return JSONResponse(content={"rules": pull_xml_from_github()})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/rule-rewriting")
def rule_rewriting(input_data: RuleInputData) -> JSONResponse:
    """
    Modify an existing rule based on input and output the new version
    """
    try:
        response, usage = rewrite_rule_helper(
            original_rule=input_data.original_rule_text,
            target_element=input_data.target_element,
            element_action=input_data.element_action,
            specific_actions=input_data.specific_actions,
        )
        response = response.replace("```xml\n", "").replace("\n```", "")
        response, usages = check_rule_modification(response)
        all_usages = [usage] + usages
        combined_usage = combine_all_usages(all_usages)
        return JSONResponse(content={"response": response, "usage": combined_usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


def process_modifications(rule_id: str, modifications: pd.DataFrame) -> Dict:
    logger.info(f"Processing {rule_id=} with modifications: {modifications=}")
    all_usages = []
    try:
        original_rule_text, original_rule_name = fetch_rule_by_id(rule_id)
        modified_rule_text = original_rule_text

        if original_rule_text:
            for _, modification in modifications.iterrows():
                modified_rule_text, usage = rewrite_rule_helper(
                    original_rule=modified_rule_text,
                    target_element=modification["target element"],
                    element_action=modification["action to take"],
                    specific_actions=modification["specific actions"],
                )
                all_usages.append(usage)

            modified_rule_text = modified_rule_text.replace("```xml\n", "").replace("\n```", "")
            modified_rule_text, usages = check_rule_modification(modified_rule_text)
            all_usages.extend(usages)
            if "<or>" in modified_rule_text:
                logger.info(f"Splitting rule {rule_id} on <or> tag...")
                split_rules, split_usages = split_rule_by_or_operands(modified_rule_text)
                modified_rule_text = "\n".join(split_rules)
                all_usages.append(split_usages)
            combined_usage = combine_all_usages(all_usages)
            return {
                "original_rule_id": rule_id,
                "original_rule_name": original_rule_name,
                "response": modified_rule_text,
                "usage": combined_usage,
            }
        else:
            logger.error(f"No rule found for id {rule_id}")
            return f"No rule found for id {rule_id}"
    except Exception as e:
        error_message = f"Error modifying rule ID {rule_id}: {e}"
        logger.error(error_message)
        logger.exception(e)
        return error_message


@app.post("/bulk-rule-rewriting")
async def bulk_rule_rewriting(csv_file: UploadFile = File(...)) -> JSONResponse:
    """
    Modify existing rules based on a CSV file input and output the new versions
    """
    try:
        # Read the CSV file into a pandas DataFrame
        csv_string = StringIO((await csv_file.read()).decode())
        df = pd.read_csv(csv_string)
    except Exception as e:
        logger.error(e)
        return JSONResponse(status_code=500, content=f"Error reading CSV {str(e)}")

    if (
        "target element" not in df.columns
        and "action to take" not in df.columns
        and "specific actions" not in df.columns
    ):
        return JSONResponse(
            status_code=500,
            content=f"Columns missing 'target element' or 'action to take' or 'specific actions', current dataset has columns: {df.columns}",
        )

    responses = []
    errors = []
    rule_modifications = df.groupby("xml rule")

    with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4)) as executor:
        # submit all matches to the executor
        future_to_match = {executor.submit(process_modifications, rule_id, modifications): rule_id for rule_id, modifications in rule_modifications}

        # collect the results from the futures as they are completed
        results = [future.result() for future in as_completed(future_to_match) if future.result() is not None]
        responses = [result for result in results if not isinstance(result, str)]
        errors = [result for result in results if isinstance(result, str)]

    status_code = 200 if responses else 500
    return JSONResponse(
        content={"results": responses, "errors": errors}, status_code=status_code
    )


@app.post("/rule-splitting")
def rule_rewriting(input_data: RuleInputData) -> JSONResponse:
    """
    Modify an existing rule based on input and output the new version
    """
    try:
        if input_data.element_action == "or":
            new_rules, usage = split_rule_by_or_operands(
                input_rule=input_data.original_rule_text,
                target_or_index=input_data.target_or_index,
            )
        elif input_data.element_action == "toobroad":
            new_rules, usage = split_broad_rule_with_instructions(
                input_data.original_rule_text,
                input_data.specific_actions[0],
            )
        # validate rules and calculate total usage
        new_rules_verified = []
        all_usages = [usage]
        for r in new_rules:
            validated_rule, _usage = check_rule_modification(r)
            new_rules_verified.append(validated_rule)
            all_usages.extend(_usage)
        combined_usage = combine_all_usages(all_usages)
        return JSONResponse(
            content={
                "response": new_rules,
                "usage": combined_usage,
            }
        )
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/update-rule")
async def update_rule(input_data: UpdateRuleInput) -> JSONResponse:
    """
    Update the rule in the repo and create a PR. Returns a link to the PR
    """
    try:
        return JSONResponse(
            content={
                "pull_request_link": update_rule_helper(
                    rules_to_update=input_data.rules_to_update
                )
            }
        )
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/create-rule")
async def create_rule(input_data: CreateRuleInput) -> JSONResponse:
    """
    Create a rule based on given input, returns the new rule and the usage
    """
    all_usages = []
    try:
        response, usage = create_rule_helper(
            ad_hoc_syntax=input_data.ad_hoc_syntax,
            rule_number=input_data.rule_number,
            correction=input_data.correction,
            category=input_data.category,
            explanation=input_data.explanation,
            test_sentence=input_data.test_sentence,
            test_sentence_correction=input_data.test_sentence_correction,
        )
        all_usages.append(usage)
        new_id = "".join(str(random.randint(0, 9)) for _ in range(40))
        response = response.replace("{new_rule_id}", f"BRIEFCATCH_{new_id}")

        if "<or>" in response:
            logger.info(f"splitting on <or> {input_data.rule_number}...")
            new_rules, split_usage = split_rule_by_or_operands(input_rule=response)
            all_usages.append(split_usage)
            validated_rules = []
            for new_rule in new_rules:
                checked_rule, check_usages = check_rule_modification(new_rule)
                validated_rules.append(checked_rule)
                all_usages.extend(check_usages)
            response = "\n".join(validated_rules)
        else:
            response, check_usages = check_rule_modification(response)
            all_usages.extend(check_usages)
                
        combined_usage = combine_all_usages(all_usages)
        return JSONResponse(content={"response": response, "usage": combined_usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


def process_rule_creation(record: Dict) -> Dict:
    """
    Helper function to process rule modification in parallel
    """
    all_usages = []
    try:
        response, usage = create_rule_helper(
            ad_hoc_syntax=record.get("ad_hoc_syntax"),
            rule_number=record.get("rule_number"),
            correction=record.get("correction"),
            category=record.get("category"),
            explanation=record.get("explanation"),
            test_sentence=record.get("test_sentence"),
            test_sentence_correction=record.get("test_sentence_correction"),
        )
        all_usages.append(usage)
        new_id = "".join(str(random.randint(0, 9)) for _ in range(40))
        response = response.replace("{new_rule_id}", f"BRIEFCATCH_{new_id}")

        if "<or>" in response:
            logger.info(f"splitting on <or> {record.get('rule_number')}...")
            new_rules, split_usage = split_rule_by_or_operands(input_rule=response)
            all_usages.append(split_usage)
            validated_rules = []
            for new_rule in new_rules:
                checked_rule, check_usages = check_rule_modification(new_rule)
                validated_rules.append(checked_rule)
                all_usages.extend(check_usages)
            response = "\n".join(validated_rules)
        else:
            response, check_usages = check_rule_modification(response)
            all_usages.extend(check_usages)
        
        new_rule_name = f"BRIEFCATCH_{record.get('category').upper()}_{record.get('rule_number')}"
        
        combined_usage = combine_all_usages(all_usages)
        return {"rule_name": new_rule_name, "rule": response, "usage": combined_usage}
    except Exception as e:
        error_message = f"Error creating new rule: {e}"
        logger.error(error_message)
        logger.exception(e)
        return {"error": error_message}


@app.post("/bulk-rule-creation")
async def bulk_rule_creation(csv_file: UploadFile = File(...)) -> JSONResponse:
    """
    Create rules based on a CSV file input and output the new rules
    """
    try:
        # Read the CSV file into a pandas DataFrame
        csv_string = StringIO((await csv_file.read()).decode())
        df = pd.read_csv(csv_string)
    except Exception as e:
        logger.error(e)
        return JSONResponse(status_code=500, content={"errors": f"Error reading CSV {str(e)}"})

    expected_columns = [
        "ad_hoc_syntax",
        "rule_number",
        "correction",
        "category",
        "explanation",
        "test_sentence",
        "test_sentence_correction",
    ]
    if (
        "ad_hoc_syntax" not in df.columns
        and "rule_number" not in df.columns
        and "correction" not in df.columns
        and "category" not in df.columns
        and "explanation" not in df.columns
        and "test_sentence" not in df.columns
        and "test_sentence_correction" not in df.columns
    ):
        return JSONResponse(
            status_code=500,
            content={"errors": f"Columns missing {' or '.join(expected_columns)}, current dataset has columns: {df.columns}"},
        )

    responses = []
    errors = []
    records = df.to_dict(orient="records")

    with ThreadPoolExecutor() as executor:
        future_to_record = {executor.submit(process_rule_creation, record): record for record in records}
        for future in as_completed(future_to_record):
            result = future.result()
            if "error" in result:
                errors.append(result["error"])
            else:
                responses.append(result)
            # record = future_to_record[future]
            # logger.info(f"Processed {record=}")

    status_code = 200 if responses else 500
    return JSONResponse(
        content={"results": responses, "errors": errors}, status_code=status_code
    )


@app.post("/ngram-analysis-suggestions")
async def ngram_analysis_suggestions(input_data: NgramInput) -> JSONResponse:
    """
    Take in the rule and perform analysis on the suggestions, returning the clusters of records from ngram
    """
    if input_data.suggestion_pattern:
        try:
            return JSONResponse(
                content=ngram_helper_suggestion(
                    input_data.rule_pattern, input_data.suggestion_pattern
                )
            )
        except Exception as e:
            logger.error(e)
            return JSONResponse(content={"error": str(e)}, status_code=500)
    return JSONResponse(
        content={"response": "Missing required field, suggestion_pattern"},
        status_code=500,
    )


@app.post("/ngram-analysis-rule")
async def ngram_analysis_rule(input_data: NgramInput) -> JSONResponse:
    """
    Take in the rule and perform analysis on the rule pattern, returning the clusters of records from ngram
    """
    try:
        return JSONResponse(content=ngram_helper_rule(input_data.rule_pattern))
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ngram-analysis")
async def ngram_analysis(input_data: InputData) -> JSONResponse:
    """
    Take in the rule and perform both analysis on it
    """
    rule_parts = input_data.input_text.split("\n")
    if len(rule_parts) == 2:
        rule_pattern = rule_parts[0]
        suggestion_pattern = rule_parts[1]
        pattern_analysis = {}
        suggestion_analysis = {}
        try:
            pattern_analysis = ngram_helper_rule(rule_pattern)
        except Exception as e:
            logger.error(f"Error analysing rule pattern {rule_pattern}: {e}")
            logger.exception(e)
        try:
            suggestion_analysis = ngram_helper_suggestion(
                rule_pattern, suggestion_pattern
            )
        except Exception as e:
            logger.error(
                f"Error analysing suggestion pattern {suggestion_pattern}: {e}"
            )
            logger.exception(e)
        return JSONResponse(
            content={
                "pattern_analysis": pattern_analysis,
                "suggestion_analysis": suggestion_analysis,
            }
        )
    return JSONResponse(
        content={
            "response": "Incorrect rule submitted, please check that it is separated into two lines"
        },
        status_code=500,
    )



def process_ngram_record(record: Dict, rule_number_key: str) -> Tuple:
    try:
        # Perform the given operations and create the result dictionary
        result = {
            "rule_number": record[rule_number_key],
            "correction_analysis": ngram_helper_suggestion(record.get("//Rule"), record.get("//Correction")),
            "rule_analysis": ngram_helper_rule(record.get("//Rule")),
        }
        return ('response', result)

    except Exception as e:
        error_message = f"Error performing ngram analysis: {e}"
        logger.error(error_message)
        logger.exception(e)
        return ('error', error_message)


@app.post("/bulk-ngram-analysis")
async def bulk_ngram_analysis(csv_file: UploadFile = File(...)) -> JSONResponse:
    """
    Do bulk ngram analysis given a file of patterns and suggestions
    """
    try:
        # Read the CSV file into a pandas DataFrame
        csv_string = StringIO((await csv_file.read()).decode())
        df = pd.read_csv(csv_string)
        df.dropna(inplace=True)
    except Exception as e:
        logger.error(e)
        return JSONResponse(status_code=500, content=f"Error reading CSV {str(e)}")

    if "//Rule" not in df.columns and "//Correction" not in df.columns:
        return JSONResponse(
            status_code=500,
            content=f"Columns missing '//Correction' or '//Rule', current dataset has columns: {df.columns}",
        )

    responses = []
    errors = []
    records = df.to_dict(orient="records")
    rule_number_key = [key for key in records[0] if "number" in key.lower()][0]

    with ThreadPoolExecutor() as executor:
        future_to_record = {executor.submit(process_ngram_record, record, rule_number_key): record for record in records}
        # retrieve results as they are completed
        for future in as_completed(future_to_record):
            result_type, result = future.result()
            if result_type == 'response':
                responses.append(result)
            elif result_type == 'error':
                errors.append(result)

    status_code = 200 if responses else 500
    return JSONResponse(
        content={"results": responses, "errors": errors}, status_code=status_code
    )


@app.post("/generate-excel")
async def generate_excel(ngram_analysis: List[Dict]):
    # Create a BytesIO buffer to write the Excel file to
    output = BytesIO()

    # Create a Pandas Excel writer using the buffer as the file to write to
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for analysis in ngram_analysis:
            rule_number = analysis["rule_number"]
            for key in ["rule_analysis", "correction_analysis"]:
                # Create a DataFrame for flags
                df_flags = create_df_from_analysis_data(analysis[key]["flags"], "flags")
                # Create a DataFrame for clusters
                df_clusters = create_df_from_analysis_data(
                    analysis[key]["clusters"], "clusters"
                )
                # Create a DataFrame for usages
                df_usages = create_df_from_analysis_data(
                    analysis[key]["usages"], "usages"
                )
                # Concatenate all DataFrames
                df = pd.concat([df_flags, df_clusters, df_usages], ignore_index=True)
                # Write the DataFrame to the Excel writer
                df.to_excel(writer, sheet_name=f"{rule_number}_{key}", index=False)

    # Seek to the beginning of the stream
    output.seek(0)

    # Create a streaming response to send back the Excel file
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
