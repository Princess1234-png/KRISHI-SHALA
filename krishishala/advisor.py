"""Rule-based multilingual crop advisor.

This is an offline, deterministic baseline. `BhashiniAdapter` documents where the
real Bhashini (ULCA/Dhruva) speech and translation calls plug in; it is a stub so
the project runs with no network or API keys.
"""
from .analytics import health_alerts

ADVICE = {
    "yellow_leaves": {
        "en": "Yellow leaves often mean nitrogen deficiency or overwatering. Check soil moisture and add compost.",
        "ta": "இலைகள் மஞ்சளாவது பொதுவாக நைட்ரஜன் குறைபாடு அல்லது அதிக நீர் காரணமாக இருக்கலாம். மண் ஈரப்பதத்தை சரிபார்த்து, மக்கிய உரம் சேர்க்கவும்.",
        "hi": "पत्तियों का पीला होना अक्सर नाइट्रोजन की कमी या अधिक पानी के कारण होता है। मिट्टी की नमी जांचें और कम्पोस्ट डालें।",
    },
    "wilting": {
        "en": "Wilting can mean water stress or root rot. Check soil moisture and temperature.",
        "ta": "இலைகள் வாடினால் மண் ஈரப்பதத்தையும் வெப்பநிலையையும் சரிபார்க்கவும்; நீர் பற்றாக்குறை அல்லது வேர் அழுகல் இருக்கலாம்.",
        "hi": "पत्ते मुरझाएं तो मिट्टी की नमी और तापमान जांचें; पानी की कमी या जड़ सड़न हो सकती है।",
    },
    "pests": {
        "en": "Remove affected leaves, spray a neem-oil solution, and contact your local KVK.",
        "ta": "பூச்சி தாக்குதல் தெரிந்தால் பாதிக்கப்பட்ட இலைகளை அகற்றி, வேப்ப எண்ணெய் கரைசலை தெளிக்கவும். உள்ளூர் KVK-வை அணுகவும்.",
        "hi": "कीट दिखें तो प्रभावित पत्ते हटाएं, नीम तेल का घोल छिड़कें और स्थानीय KVK से संपर्क करें।",
    },
}

KEYWORDS = {
    "yellow_leaves": ("yellow", "மஞ்சள்", "पीला", "पीली"),
    "wilting": ("wilt", "droop", "வாடு", "வாடி", "मुरझा"),
    "pests": ("pest", "insect", "bug", "பூச்சி", "कीट"),
}

# Month -> crops suited to sow (illustrative; replace with agro-climatic zone data).
SEASONAL_CROPS = {
    "kharif": ("rice",), "rabi": ("wheat", "spinach"), "zaid": ("tomato",),
}


def season_for_month(month):
    if 6 <= month <= 10:
        return "kharif"
    if month >= 11 or month <= 3:
        return "rabi"
    return "zaid"


def what_to_plant(month):
    return list(SEASONAL_CROPS[season_for_month(month)])


def classify(question):
    text = question.lower()
    for topic, words in KEYWORDS.items():
        if any(w in text for w in words):
            return topic
    return None


def advise(question, lang="en", latest_reading=None):
    """Return {'topic', 'answer', 'sensor_alerts'}. Falls back to English, then a referral."""
    topic = classify(question)
    if topic:
        table = ADVICE[topic]
        answer = table.get(lang) or table["en"]
    else:
        answer = "I could not identify the problem. Please describe the symptom or ask your Krishi Guru / KVK."
    alerts = health_alerts(latest_reading) if latest_reading else []
    return {"topic": topic, "answer": answer, "sensor_alerts": alerts}


class BhashiniAdapter:
    """Stub for Bhashini integration (ASR -> translate -> advise -> translate -> TTS).

    Implement `translate`/`speech_to_text`/`text_to_speech` against the Bhashini
    Dhruva API using credentials you obtain from bhashini.gov.in. Intentionally
    unimplemented here so the repo has no secrets and no network dependency.
    """

    def speech_to_text(self, audio_bytes, lang):
        raise NotImplementedError("Wire up Bhashini ASR here")

    def translate(self, text, source_lang, target_lang):
        raise NotImplementedError("Wire up Bhashini NMT here")

    def text_to_speech(self, text, lang):
        raise NotImplementedError("Wire up Bhashini TTS here")
