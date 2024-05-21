import streamlit as st
import pandas as pd
import numpy as np
import time
import sounddevice as sd
import soundfile as sf
import pygame
from queue import Queue
from dotenv import load_dotenv 
import os
import requests
from st_pages import Page, Section, show_pages, add_page_title

load_dotenv()

st.title('Playing Guitar!')

# Initialize pygame for MIDI playback
pygame.mixer.init()
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

midi_queue = Queue()

def list_devices():
    name_dict = {}
    devices = sd.query_devices()
    i = 0
    for index, device in enumerate(devices):
        name_dict[device['name']] = i
        i += 1
    return name_dict

def record_audio(device_index, duration=10, sample_rate=44100):
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, device=device_index, dtype='float32')
        sd.wait()  # Wait until recording is finished
        output_file = 'recorded_sample/output.wav'
        os.makedirs('recorded_sample', exist_ok=True)
        sf.write(output_file, audio_data, sample_rate)
        return output_file
    except Exception as e:
        st.error(f'An error occurred: {e}')
        return None

def stop_midi():
    pygame.mixer.music.stop()
    with midi_queue.mutex:
        midi_queue.queue.clear()
    st.write("Stopped all MIDI playback and cleared the queue")

def genrate_midi_and_play_queue():
    while not midi_queue.empty() or st.session_state.get("Start", False):
        if midi_queue.empty():
            time.sleep(1)
            continue
        midi_file = midi_queue.get()
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        recorded_file = record_audio(input_device_index, duration=10, sample_rate=44100)
        if recorded_file:
            url = os.getenv('URL')  # Replace with your server URL
            url = url + "/process-audio"
            with open(recorded_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    with open("output.mid", 'wb') as mid_file:
                        mid_file.write(response.content)
                    midi_queue.put("output.mid")
                else:
                    st.error('Failed to upload file to the server')
        
    while pygame.mixer.music.get_busy():
        print("busy")
        pygame.time.wait(100)

# Register the event handler for the end of midi playback
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)


with st.container():
    try:
        ele = list_devices()
        input_option = st.selectbox(
            "Please Select Input Device.",
            (ele.keys()))

        output_option = st.selectbox(
            "Please Select Output Device",
            (ele.keys()))
        
        input_device_index = ele.get(input_option)
        output_device_index = ele.get(output_option)

        # Load the initial MIDI file into the queue
        midi_path = 'first.mid'  # Ensure 'first.mid' exists in the working directory
        midi_queue.put(midi_path)
        
        col1, col2 = st.columns([0.2, 1.4])
        with col1:
            if st.button("Start"):
                st.session_state["Start"] = True
                st.session_state["Stop"] = False
                with st.spinner("initial setting..."):
                    url = os.getenv('URL')  # Replace with your server URL
                    url = url + "/init-audio"
                    with open("recoded_sample/first.wav", 'rb') as f:
                        files = {'file': f}
                        response = requests.post(url, files=files)
                        if response.status_code == 200:
                            with open("first.mid", 'wb') as mid_file:
                                mid_file.write(response.content)
                genrate_midi_and_play_queue()

        with col2:
            if st.button("Stop"):
                st.session_state["Stop"] = True
                st.session_state["Start"] = False
                stop_midi()

        # Event handling loop
        while st.session_state.get("Start", False):
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    genrate_midi_and_play_queue()
            time.sleep(0.1)  # To prevent busy waiting
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
