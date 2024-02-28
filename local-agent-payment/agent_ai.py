import asyncio

import requests
import time
import json

from google.cloud import texttospeech
from google.cloud import speech

from models import summarize_agent_response
from models import interprete_user_answer
from record_audio import record_audio
from speech_text_convert import convert_text_to_speech
from speech_text_convert import convert_speech_to_text
from speech_text_convert import output_voice
from sdvlink_companion import show_notification, hide_notification


EMAIL = "devstar2156@gcplab.me"
REQUESTED_MODEL = "talkative-01"
BEARER_TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3MDkxMTg1MTQsImlhdCI6MTcwOTExNDkxNCwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiIxYWNiZDY3NzNlMTg1ZDRjOWM2MjdiNTIiLCJzY29wZSI6IiIsInN1YiI6IjgxNmQzNTk3NTI5MDNiMmI4YTA0NGQwYzc5NDQxYjBkNDI1NzBhMDk1Y2U1MjM4ZCJ9.VnwgpTiE-3X0oJwf-ix1yNj_cWncJvI2qhh93NzchIK9rhj3whf9fI1HIUifwMAoj8o7xR70zyrgtkYPKIQzHuOdBe_s7FbGWGGLSb696z2PPtB53YicdRPPTmkPVmD_7EttmO1W57GdvE9F1HIAumI4OnIxMEuZONOQD61C9KbO7jyC4XfFKpy0uyaZnJ1urxYNlGlzvT58iEODnpjjmRI9vyirHC-dAHadSsxq05Hd8dQgFDHeO5pIdhUOYB33JjjolTvVgED21IL7r7xIXtPyUKc6cc-OpMWrULZptasLjNro9NogwbSd5kXfLIF0F4CyRqOU2Gspv1FtLJ-kBw"


def start_session(bearer_token, email, requestedModel):
    data = {
        "email": email,
        "requestedModel": requestedModel
    }
    session = requests.post("https://agentverse.ai/v1beta1/engine/chat/sessions", json=data, headers={
        "Authorization": f"bearer {bearer_token}"
    })
    print(session.json())
    return session.json()


def send_start_message(bearer_token, session_id, message):
    data = {
        "payload": {
            "type": "start",
            "objective": message,
            "context": "User full Name: Test User\nUser email: user@user.com\nUser location: latitude=51.5072, longitude=0.1276\n"
        }
    }
    pathParameters = {
        "session_id": session_id
    }
    requests.post(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{pathParameters['session_id']}/submit",
                  json=data, headers={
            "Authorization": f"bearer {bearer_token}"
        })


def send_user_json_message(bearer_token, session_id, message):
    data = {
        "payload": {
            "type": "user_json",
            "messag_id": message,
            "user_json": {
                "type": "task_list",
                "selection": [
                    "0"
                ]
            }
        }
    }

    pathParameters = {
        "session_id": session_id
    }

    requests.post(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{pathParameters['session_id']}/submit",
                  json=data, headers={
            "Authorization": f"bearer {bearer_token}"
        })


def fetch_new_messages(bearer_token, session_id, client):
    start_time = time.time()  # Initialize start time
    fetch_timeout = 40  # Set your desired timeout duration in seconds
    response = None

    print(f"Fetching new messages for session {session_id}...")
    flag = False
    while not flag:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time // 8 > (elapsed_time - 0.1) // 8:
            in_between_message = "I am still searching for charging stations on your route."
            audio_file = convert_text_to_speech(client, in_between_message)
            output_voice(audio_file)

        try:
            start_fetch_time = time.time()
            pathParameters = {
                "session_id": session_id
            }
            response = requests.get(
                f"https://agentverse.ai/v1beta1/engine/chat/sessions/{pathParameters['session_id']}/responses",
                headers={
                    "Authorization": f"bearer {bearer_token}"
                })

            response_data = json.loads(response.text)
            response_list = response_data["agent_response"]
            for item in response_list:
                item_dict = json.loads(item)
                if item_dict.get("type") == "agent_json":
                    print("Response received: ", item_dict.get("agent_json"))
                    flag = True
                    return item_dict.get("agent_json")
                elif item_dict.get("type") == "agent_message":
                    print("Response received: ", item_dict.get("agent_message"))
                    flag = True
                    return item_dict.get("agent_message")
                else:
                    print(f"No response received. Continuing...")

                # Adjust sleep time based on fetch duration to maintain consistent interval
            fetch_duration = time.time() - start_fetch_time
            if flag:
                break
            time.sleep(max(5 - fetch_duration, 0))  # Ensures at least some delay

            if time.time() - start_time > fetch_timeout:
                print("Fetch timeout reached. Exiting loop.")
                break

        except Exception as e:  # Consider catching more specific exceptions if possible
            print(f"An error occurred: {e}")
            break

    return response.json() if response else None


async def look_for_charging_station(bearer_token, email, requestedModel, text_to_speech_client):
    confirm_message = "Ok, I will look for charging stations on your route that meet your personal preferences."
    await notify_ui(confirm_message)
    audio_file = convert_text_to_speech(text_to_speech_client, confirm_message)
    output_voice(audio_file)
    await hide_ui()

    session = start_session(bearer_token, email, requestedModel)
    session_id = session["session_id"]
    print(f"Session started successfully with ID: {session_id}")
    print()

    input_message = "Please find a Bosch charging station on my route that meets my personal preferences."
    print(f"Sending start message: {input_message}\n")
    send_start_message(bearer_token, session_id, input_message)

    answer_message = fetch_new_messages(bearer_token, session_id, text_to_speech_client)
    if answer_message:
        send_user_json_message(bearer_token, session_id, "0")

    charging_request_response = fetch_new_messages(bearer_token, session_id, text_to_speech_client)

    if charging_request_response:
        response_summary = summarize_agent_response(charging_request_response, input_message)
        print(response_summary)
        await notify_ui(response_summary)
        convert_text_to_speech(text_to_speech_client, response_summary)
        output_voice(audio_file)
        await hide_ui()
    else:
        print("No response received - stopping.")
        response_message = "Sorry, I could not find a solution for your request. Please try again later."
        await notify_ui(response_message)
        audio_file = convert_text_to_speech(text_to_speech_client, response_message)
        output_voice(audio_file)
        await hide_ui()


async def act_on_user_answer(find_charging_station, num_tries, bearer_token, email, requestedModel,
                             text_to_speech_client,
                             speech_to_text_client):
    if find_charging_station == "yes" or find_charging_station == "Yes":
        await look_for_charging_station(bearer_token, email, requestedModel, text_to_speech_client)

    elif find_charging_station == "no" or find_charging_station == "No":
        decline_message = "Ok, I will not look for charging stations on your route, right now. I will ask you again when the battery is below 10%."
        await notify_ui(decline_message)
        audio_file = convert_text_to_speech(text_to_speech_client, decline_message)
        output_voice(audio_file)
        await hide_ui()
    else:
        if num_tries < 2:
            num_tries += 1
            invalid_message = "Sorry, I did not understand your answer. Do you want me to find a charging station on your route?"
            await notify_ui(invalid_message)
            audio_file = convert_text_to_speech(text_to_speech_client, invalid_message)
            output_voice(audio_file)
            await hide_ui()

            speech_file = record_audio()
            user_answer = convert_speech_to_text(speech_file, speech_to_text_client)
            find_charging_station = interprete_user_answer(user_answer)
            await act_on_user_answer(find_charging_station, num_tries, bearer_token, email, requestedModel,
                                     text_to_speech_client, speech_to_text_client)

        else:
            invalid_message = "Sorry, I could not understand your answer. I will ask you again when the battery is below 10%."
            await notify_ui(invalid_message)
            audio_file = convert_text_to_speech(text_to_speech_client, invalid_message)
            output_voice(audio_file)
            await hide_ui()
            print(invalid_message)


async def notify_ui(text, header="Notification"):
    await show_notification(header, text)


async def hide_ui():
    await hide_notification()


async def stage_1(text_to_speech_client, speech_to_text_client):
    num_tries = 1
    bearer_token = BEARER_TOKEN
    email = EMAIL
    requestedModel = REQUESTED_MODEL

    print("Starting session...")

    print("Sir, your battery is below 20%. Do you want me to find a charging station on your route?")
    starting_output = "Sir, your battery is below 20%. Do you want me to find a charging station on your route?"
    await notify_ui(starting_output)
    audio_file = convert_text_to_speech(text_to_speech_client, starting_output)
    output_voice(audio_file)
    await hide_ui()

    speech_file = record_audio()
    print("Audio recorded successfully.")
    user_answer = convert_speech_to_text(speech_file, speech_to_text_client)
    find_charging_station = interprete_user_answer(user_answer)

    await act_on_user_answer(find_charging_station, num_tries, bearer_token, email, requestedModel,
                             text_to_speech_client, speech_to_text_client)
    
    speech_file = record_audio()
    user_answer = convert_speech_to_text(speech_file, speech_to_text_client)
    find_charging_station = interprete_user_answer(user_answer)
    confirm_message = "Ok Sir, I reserved a spot for you and started the navigation to the charging station."
    await notify_ui(confirm_message)
    audio_file = convert_text_to_speech(text_to_speech_client, confirm_message)
    output_voice(audio_file)
    await hide_ui()

if __name__ == "__main__":
    text_to_speech_client = texttospeech.TextToSpeechClient()
    speech_to_text_client = speech.SpeechClient()

    asyncio.run(stage_1(text_to_speech_client, speech_to_text_client))
