import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import numpy as np
from PIL import Image
import time

# Initialize the speech recognizer
recognizer = sr.Recognizer()

def text_to_speech_urdu(text):
    """Convert text to Urdu speech and play it using Streamlit"""
    try:
        tts = gTTS(text=text, lang='ur')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")
        text_to_speech_urdu(f"خطا: {str(e)}")

def speech_to_text():
    """Convert speech to text with improved handling"""
    with sr.Microphone() as source:
        st.write("Checking microphone... Please ensure it’s working and in a quiet environment.")
        try:
            # Test microphone with a short listen
            audio_test = recognizer.listen(source, timeout=3)
            st.write("Microphone is working. Listening... Please start speaking.")
        except sr.WaitTimeoutError:
            st.error("Microphone test failed. Please check your microphone and try again.")
            text_to_speech_urdu("مائیکروفون کام نہیں کر رہا۔ براہ کرم چیک کریں۔")
            return None

        recognizer.adjust_for_ambient_noise(source, duration=4)  # Adjust for background noise
        st.write("Please wait 2 seconds after the question before speaking.")
        time.sleep(2)  # Give time for audio to stop

        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=15)  # Increased timeout
            text = recognizer.recognize_google(audio, language='ur-PK')
            return text
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please speak clearly and slowly.")
            text_to_speech_urdu("آڈیو سمجھ نہیں آئی۔ براہ کرم صاف اور آہستہ بولیں۔")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results. Please check your internet connection: {e}")
            text_to_speech_urdu("نتیجہ حاصل نہیں ہو سکا۔ براہ کرم اپنا انٹرنیٹ چیک کریں۔")
            return None
        except sr.WaitTimeoutError:
            st.error("Listening timed out. Please speak within 15 seconds and try again.")
            text_to_speech_urdu("سماعت کا وقت ختم ہو گیا۔ براہ کرم 15 سیکنڈ کے اندر بولیں۔")
            return None
        except Exception as e:
            st.error(f"Error in speech-to-text: {e}")
            text_to_speech_urdu(f"خطا: {str(e)}")
            return None

def capture_photo():
    """Capture a photo using the webcam or upload a photo"""
    st.write("آپ اپنی تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
    captured_image = st.camera_input("Capture your photo using the webcam")
    if captured_image is not None:
        image = Image.open(captured_image)
        return np.array(image)

    uploaded_file = st.file_uploader("Alternatively, upload your photo", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        return np.array(image)

    return None

def convert_urdu_number(urdu_text):
    """Helper function to convert Urdu numbers to integers"""
    urdu_to_eng = {
        'ایک': 1, 'دو': 2, 'تین': 3, 'چار': 4, 'پانچ': 5, 'چھ': 6, 'سات': 7, 'آٹھ': 8, 'نو': 9, 'دس': 10,
        'گیارہ': 11, 'بارہ': 12, 'تیرہ': 13, 'چودہ': 14, 'پندرہ': 15, 'سولہ': 16, 'سترہ': 17, 'اٹھارہ': 18,
        'انیس': 19, 'بیس': 20, 'تیس': 30, 'چالیس': 40, 'پچاس': 50, 'ساٹھ': 60
    }
    return urdu_to_eng.get(urdu_text, int(urdu_text)) if urdu_text.isdigit() else urdu_to_eng.get(urdu_text)

def main():
    st.title("اردو رجسٹریشن فارم")
    st.write("Welcome to Urdu Registration Form")

    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.responses = {}

    if st.session_state.step == 0:
        if st.button("شروع کریں (Start)"):
            text_to_speech_urdu("آپ کا نام کیا ہے؟")
            st.session_state.step = 1

    elif st.session_state.step == 1:
        st.write("آپ کا نام کیا ہے؟")
        if st.button("بولیں (Speak)"):
            name = speech_to_text()
            if name:
                st.session_state.responses['name'] = name
                st.write(f"آپ کا نام: {name}")
                st.session_state.step = 2
                text_to_speech_urdu("آپ کی عمر کیا ہے؟")
        if st.button("دستی درج کریں (Enter Manually)"):
            name = st.text_input("نام درج کریں", key="manual_name")
            if name:
                st.session_state.responses['name'] = name
                st.session_state.step = 2
                text_to_speech_urdu("آپ کی عمر کیا ہے؟")

    elif st.session_state.step == 2:
        if 'age_question_asked' not in st.session_state:
            text_to_speech_urdu("آپ کی عمر کیا ہے؟")
            st.session_state.age_question_asked = True
        
        st.write("آپ کی عمر کیا ہے?")
        
        if st.button("بولیں (Speak)", key="speak_age_button"):
            age_text = speech_to_text()
            if age_text:
                st.write(f"شناخت شدہ عمر: {age_text}")
                try:
                    age = convert_urdu_number(age_text)
                    if age > 60:
                        st.error("معذرت، آپ کی عمر زیادہ ہے")
                        text_to_speech_urdu("معذرت، آپ کی عمر زیادہ ہے")
                        del st.session_state.age_question_asked
                        st.session_state.step = 0
                    else:
                        st.success(f"عمر محفوظ ہو گئی: {age}")
                        st.session_state.responses['age'] = age
                        st.session_state.step = 3
                        del st.session_state.age_question_asked
                        st.rerun()
                except (ValueError, TypeError):
                    st.error(f"نہیں سمجھ سکا: '{age_text}'. براہ کرم دوبارہ کوشش کریں")
                    text_to_speech_urdu("براہ کرم دوبارہ عمر بولیں")
        if st.button("دستی درج کریں (Enter Manually)", key="manual_age"):
            age = st.number_input("عمر درج کریں", min_value=1, max_value=60, key="manual_age_input")
            if age:
                st.success(f"عمر محفوظ ہو گئی: {age}")
                st.session_state.responses['age'] = age
                st.session_state.step = 3
                st.rerun()

    elif st.session_state.step == 3:
        st.write("آپ کی جنس کیا ہے؟")
        if st.button("بولیں (Speak)", key="speak_gender_button"):
            gender = speech_to_text()
            if gender:
                st.session_state.responses['gender'] = gender
                st.write(f"آپ کی جنس: {gender}")
                st.session_state.step = 4
                text_to_speech_urdu("آپ کے سربراہ کا شناختی کارڈ نمبر کیا ہے؟")
                st.rerun()
        if st.button("دستی درج کریں (Enter Manually)", key="manual_gender"):
            gender = st.text_input("جنس درج کریں (مرد/عورت)", key="manual_gender_input")
            if gender:
                st.session_state.responses['gender'] = gender
                st.session_state.step = 4
                text_to_speech_urdu("آپ کے سربراہ کا شناختی کارڈ نمبر کیا ہے؟")
                st.rerun()

    elif st.session_state.step == 4:
        st.write("آپ کے سربراہ کا شناختی کارڈ نمبر کیا ہے؟")
        nic = st.text_input("NIC Number", key="nic")
        if st.button("Next", key="nic_next_button"):
            if len(nic) == 13 and nic.isdigit():
                st.session_state.responses['nic'] = nic
                st.session_state.step = 5
                text_to_speech_urdu("براہ کرم اپنی تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
                st.rerun()
            else:
                st.error("براہ کرم درست شناختی کارڈ نمبر درج کریں")
                text_to_speech_urdu("براہ کرم درست شناختی کارڈ نمبر درج کریں")

    elif st.session_state.step == 5:
        st.write("اپنی تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
        photo = capture_photo()
        if photo is not None:
            st.image(photo, caption="آپ کی تصویر")
            st.session_state.responses['photo'] = photo
            st.session_state.step = 6
            st.rerun()
        else:
            st.error("براہ کرم تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
            text_to_speech_urdu("براہ کرم تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")

    elif st.session_state.step == 6:
        st.success("رجسٹریشن مکمل ہو گئی!")
        text_to_speech_urdu("آپ کی رجسٹریشن مکمل ہو گئی ہے۔ شکریہ")
        st.write("### Submitted Information:")
        for key, value in st.session_state.responses.items():
            if key != 'photo':
                st.write(f"{key}: {value}")
        if 'photo' in st.session_state.responses:
            st.image(st.session_state.responses['photo'], caption="Captured Photo")

        if st.button("نئی رجسٹریشن (New Registration)"):
            st.session_state.step = 0
            st.session_state.responses = {}
            st.rerun()

if __name__ == "__main__":
    main()