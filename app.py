import streamlit as st
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import speech_recognition as sr
import os

# Page configuration
st.set_page_config(page_title="🎓 ROPHI Language Translator", layout="wide", page_icon="🗣️")

# Translator setup
translator = Translator()
lang_dict = LANGUAGES
lang_list = list(lang_dict.values())

# Session state setup
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "trigger_translate" not in st.session_state:
    st.session_state.trigger_translate = False

# ---- FUNCTIONS ----
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak Now")
        try:
            audio = r.listen(source, timeout=5)
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            st.warning("Could not understand audio.")
        except sr.WaitTimeoutError:
            st.warning("Timeout: No speech detected.")
        except Exception as e:
            st.error(f"Microphone error: {e}")
        return ""

def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    path = "audio.mp3"
    tts.save(path)
    with open(path, "rb") as file:
        st.audio(file.read(), format="audio/mp3")
    os.remove(path)

# ---- TITLE SECTION ----
st.markdown("""
    <h1 style='text-align: center;'> 🎓  ROPHI Language Translator</h1>
    <p style='text-align: center; font-size: 18px; font-style: italic; color: #555; margin-top: -10px;'>
        "Speak once, be understood everywhere."
    </p>
    <hr style='margin-top: 0px;'>
""", unsafe_allow_html=True)

# ---- LAYOUT: Input (left), Output (right) ----
col1, col2 = st.columns([1, 2], gap="large")

# ---- LEFT: Input Section ----
with col1:
    st.subheader("📝 YOUR PREFERENCE ")

    if st.button("🎙️ Speak Now"):
        spoken = speech_to_text()
        if spoken:
            st.session_state.spoken_text = spoken
            st.success("Speech captured!")

    if st.button("❌ Clear Input"):
        st.session_state.spoken_text = ""

    text = st.text_area("Enter or Speak Text", value=st.session_state.spoken_text, height=150)

    auto_detect = st.checkbox("Auto-detect Source Language", value=True)
    if not auto_detect:
        source_lang = st.selectbox("Source Language", lang_list, index=lang_list.index("english"))
    target_lang = st.selectbox("Target Language", lang_list, index=lang_list.index("hindi"))

    if st.button("🔁 Translate Now"):
        st.session_state.trigger_translate = True
        st.session_state.spoken_text = text

# ---- RIGHT: Output Section ----
with col2:
    st.subheader("🌐 Translation Output")

    if st.session_state.trigger_translate:
        if not text.strip():
            st.warning("Please enter or speak some text.")
        else:
            try:
                tgt_code = list(lang_dict.keys())[list(lang_dict.values()).index(target_lang.lower())]

                if auto_detect:
                    result = translator.translate(text, dest=tgt_code)
                    src_lang_name = LANGUAGES.get(result.src, "Unknown").capitalize()
                else:
                    src_code = list(lang_dict.keys())[list(lang_dict.values()).index(source_lang.lower())]
                    result = translator.translate(text, src=src_code, dest=tgt_code)
                    src_lang_name = source_lang.capitalize()

                translated_text = result.text

                st.success("✅ Translation Complete!")
                st.markdown(f"**Detected Language:** `{src_lang_name}`")
                st.text_area("Translated Text", translated_text, height=150)

                st.subheader("🔊 Listen to Translation")
                text_to_speech(translated_text, tgt_code)

                # Save to history
                history_entry = f"{src_lang_name} → {target_lang.capitalize()}: {translated_text}"
                st.session_state.history.append(history_entry)

            except Exception as e:
                st.error(f"Translation error: {e}")

        st.session_state.trigger_translate = False

# ---- Translation History ----
st.markdown("---")
st.subheader("📜 Translation History")

if st.session_state.history:
    for item in st.session_state.history[-5:][::-1]:
        st.write(f"- {item}")
    history_text = "\n".join(st.session_state.history)
    st.download_button("📥 Download History", history_text, file_name="translation_history.txt")
else:
    st.info("No translation history yet.")

# ---- Thank You Message ----
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 16px; color: gray;'>
        🙏 Thank you for using the ROPHI Language Translator. We hope it helps you connect better with the world.
    </p>
""", unsafe_allow_html=True)
