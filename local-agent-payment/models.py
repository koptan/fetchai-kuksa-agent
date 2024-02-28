import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


EXTRACT_STATIONS_PROMPT = """
You are a Large Language Model that is part of a multi-agent system. Your task is to summarize an agent response that is formatted as a JSON object. \
The object may contain items with multiple keys and is the answer to a user input that the agent was prompted with. Find the user input and the agent \
response below and summarize the agent response with respect to the user input. Output your response in the format specified under OUTPUT_FORMAT.\

INPUT_TEXT:
{input_text}

AGENT_RESPONSE:
{agent_response}

OUTPUT_FORMAT:
* Write the summary in the style as if you were the assistant agent responding to the user input.
* List all options that you found with its respective values in a numbered list so the user can select the desired option.
* Ask the user in the end if you should reserve a spot at the first option.
* It should be polite and also feel like a natural dialogue response.
* Only output the summary and do not include other content in your response.

"""


INTERPRETE_USER_ANSWER = """
You are a Large Language Model that is part of a multi-agent system. Your task is to interprete a user's answer as confirmation or decline. You are \
provided with the exact words that the user said under USER_ANSWER. You must interprete the user's answer and respond only with one word. Give your response in the format \
specified under OUTPUT_FORMAT. Carefully read the user's answer.

USER_ANSWER:
{user_answer}

OUTPUT_FORMAT:
* If the user's answer is neither a confirmation nor a decline, respond with "invalid".
* If the user's answer is a confirmation, respond with "yes".
* If the user's answer is a decline, respond with "no".
* Only output the slected word and do not include any other content in your response.
"""


def generate(model, formatted_prompt):

    response = model.generate_content(
    [formatted_prompt],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    stream=False,
    )

    # for response in responses:
    #     print(response.text, end="")
    return response


def interprete_user_answer(user_answer):
    vertexai.init(project="bosch-bcx-hack24ber-2312", location="us-central1")
    model = GenerativeModel("gemini-1.0-pro-vision-001")
    prompt = INTERPRETE_USER_ANSWER.format(user_answer=user_answer)
    response = generate(model, prompt)
    return response.text


def summarize_agent_response(agent_response, input_prompt):
    vertexai.init(project="bosch-bcx-hack24ber-2312", location="us-central1")
    model = GenerativeModel("gemini-1.0-pro-vision-001")
    prompt = EXTRACT_STATIONS_PROMPT.format(input_text=input_prompt, agent_response=agent_response)
    response = generate(model, prompt)
    return response.text