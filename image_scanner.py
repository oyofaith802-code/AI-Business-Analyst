import os
import tempfile

import pandas as pd
import easyocr


# ============================================================
# OCR READER
# ============================================================

_reader = None


def get_reader():
    global _reader

    if _reader is None:
        _reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

    return _reader


# ============================================================
# EXTRACT TEXT FROM IMAGE
# ============================================================

def extract_text_from_image(image_path):

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    reader = get_reader()

    results = reader.readtext(
        image_path,
        detail=0,
        paragraph=True
    )

    text = "\n".join(
        str(item).strip()
        for item in results
        if str(item).strip()
    )

    if not text.strip():
        raise ValueError(
            "No readable text was found in the image."
        )

    return text


# ============================================================
# CONVERT OCR TEXT TO BUSINESS DATA
# ============================================================

def scan_business_record(image_path):

    text = extract_text_from_image(
        image_path
    )

    from natural_language_data import (
        parse_business_text
    )

    dataframe = parse_business_text(
        text
    )

    if dataframe is None:
        raise ValueError(
            "Aloko could not organize the scanned information."
        )

    if not isinstance(
        dataframe,
        pd.DataFrame
    ):
        raise TypeError(
            "Business parser did not return a DataFrame."
        )

    if dataframe.empty:
        raise ValueError(
            "No business records could be extracted."
        )

    return {
        "text": text,
        "dataframe": dataframe
    }