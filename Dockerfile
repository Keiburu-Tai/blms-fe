FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libasound2-dev \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install st-pages sounddevice soundfile streamlit streamlit_webrtc bokeh streamlit-bokeh-events

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]