import os
import tempfile

from faster_whisper import WhisperModel


# ============================================================
# WHISPER CONFIGURATION
# ============================================================

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "base"
)

_model = None


# ============================================================
# LOAD WHISPER
# ============================================================

def get_whisper_model():

    global _model

    if _model is None:

        _model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )

    return _model


# ============================================================
# TRANSCRIBE AUDIO
# ============================================================

def transcribe_audio(audio_path):

    if not os.path.exists(audio_path):

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    model = get_whisper_model()

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    )

    text = text.strip()

    if not text:

        raise ValueError(
            "No speech could be detected in the audio."
        )

    return {
        "text": text,
        "language": info.language,
        "language_probability": info.language_probability
    }


# ============================================================
# TRANSCRIBE AND ORGANIZE BUSINESS DATA
# ============================================================

def process_voice_business_data(audio_path):

    result = transcribe_audio(
        audio_path
    )

    from natural_language_data import (
        parse_business_text
    )

    dataframe = parse_business_text(
        result["text"]
    )

    if dataframe is None:

        raise ValueError(
            "Aloko could not organize the spoken information."
        )

    return {
        "text": result["text"],
        "language": result["language"],
        "dataframe": dataframe
    }