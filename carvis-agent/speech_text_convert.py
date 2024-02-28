"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
import pygame
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud import storage



def convert_text_to_speech(client, text):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    audio_file_path = "output.mp3"

    # The response's audio_content is binary.
    with open(audio_file_path, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

    return audio_file_path


def convert_speech_to_text(speech_file, client) -> speech.RecognizeResponse:
    # Instantiates a client

    # The name of the audio file to transcribe
    # gcs_uri = "output.mp3"
    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()


    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)
    transcript = response.results[0].alternatives[0].transcript
    print(f"Transcript: {transcript}")
    
    return transcript


def output_voice(audio_file):
    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the MP3 music file
    pygame.mixer.music.load(audio_file)

    # Start playing the music
    pygame.mixer.music.play()

    # Keep the script running until the music stops
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Stop the music after it's done playing
    pygame.mixer.music.stop()

    # Unload the music file to release the file resource
    pygame.mixer.music.unload()


# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     """Uploads a file to the bucket."""
#     # The ID of your GCS bucket
#     bucket_name = "carvis-audio-samples"

#     # The path to your file to upload
#     source_file_name = "output.mp3"

#     # The ID of your GCS object
#     # destination_blob_name = "storage-object-name"

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)

#     blob.upload_from_filename(source_file_name)

#     print(
#         f"File {source_file_name} uploaded to {destination_blob_name}."
#     )

#     # Example usage
#     bucket_name = 'your-bucket-name'  # Replace with your bucket name
#     source_file_name = 'local-file-to-upload.txt'  # Replace with the path to your file
#     destination_blob_name = 'destination-name-in-bucket.txt'  # Replace with the desired path in the bucket

# #upload_blob(bucket_name, source_file_name, destination_blob_name)



def main():
    # Instantiates a client

    text = "I have found a charging station on your road that meets your personal preferences. It is 5.4 kilometers away and charges 0.87 Cent per KWh. Do you want me to reserve a spot there?"




if __name__ == "__main__":
    main()
