import pyaudio
import wave

def record_audio(record_seconds=4, output_file='output.wav'):
    # Setup channel, rate, and chunk size for recording
    FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
    CHANNELS = 1              # Number of audio channels (1 for mono)
    RATE = 16000              # Sample rate (samples per second)
    CHUNK = 1024              # Number of frames per buffer

    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Concatenate all the audio frames and return
    audio_data = b''.join(frames)
    
    # Save the recorded data as a WAV file
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()

    print("Audio saved as output.wav")
    
    return output_file
