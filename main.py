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

def speech_to_text():
    """Convert speech to text with improved handling and debugging"""
    with sr.Microphone() as source:
        st.write("مائیکروفون چیک ہو رہا ہے... براہ کرم یقینی بنائیں کہ یہ کام کر رہا ہے۔")
        retries = 2
        for attempt in range(retries):
            try:
                audio_test = recognizer.listen(source, timeout=3)
                st.write("مائیکروفون کام کر رہا ہے۔ اب سنیں... براہ کرم بولنا شروع کریں۔")
                break
            except sr.WaitTimeoutError:
                if attempt < retries - 1:
                    st.warning("مائیکروفون ٹیسٹ ناکام۔ دوبارہ کوشش کر رہا ہوں...")
                    text_to_speech_urdu("مائیکروفون ٹیسٹ ناکام۔ دوبارہ کوشش کر رہا ہوں۔")
                    time.sleep(1)
                else:
                    st.error("مائیکروفون ٹیسٹ ناکام ہو گیا۔ براہ کرم اپنا مائیکروفون چیک کریں۔")
                    text_to_speech_urdu("مائیکروفون کام نہیں کر رہا۔ براہ کرم چیک کریں۔")
                    return None

        # Adjust settings for better speech detection
        recognizer.energy_threshold = 300
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.pause_threshold = 1.0
        st.write(f"Debug: Energy threshold set to {recognizer.energy_threshold}")
        st.write(f"Debug: Pause threshold set to {recognizer.pause_threshold}")

        st.write("سوال کے بعد 2 سیکنڈ انتظار کریں پھر بولیں۔")
        time.sleep(2)

        listen_retries = 2
        for attempt in range(listen_retries):
            try:
                st.write(f"کوشش {attempt + 1}: آواز سن رہا ہوں...")
                audio = recognizer.listen(source, timeout=20, phrase_time_limit=30)
                st.write("Debug: آواز کامیابی سے کیپچر ہوئی۔ گوگل API کو بھیج رہا ہوں...")
                text = recognizer.recognize_google(audio, language='ur-PK')
                st.write(f"Debug: شناخت شدہ متن: {text}")
                return text
            except sr.UnknownValueError:
                if attempt < listen_retries - 1:
                    st.warning("آواز سمجھ نہیں آئی۔ دوبارہ کوشش کریں... براہ کرم بلند آواز میں بولیں۔")
                    text_to_speech_urdu("آواز سمجھ نہیں آئی۔ دوبارہ کوشش کریں۔")
                    time.sleep(1)
                else:
                    st.error("آواز سمجھ نہیں آئی۔ براہ کرم صاف اور اردو میں بولیں، یا دستی درج کریں۔")
                    text_to_speech_urdu("آواز سمجھ نہیں آئی۔ براہ کرم صاف اور اردو میں بولیں۔")
                    return None
            except sr.RequestError as e:
                st.error(f"نتیجہ حاصل نہیں ہو سکا۔ انٹرنیٹ چیک کریں: {e}")
                text_to_speech_urdu("انٹرنیٹ کنکشن چیک کریں۔")
                return None
            except sr.WaitTimeoutError:
                if attempt < listen_retries - 1:
                    st.warning("سماعت کا وقت ختم ہو گیا۔ دوبارہ کوشش کریں...")
                    text_to_speech_urdu("سماعت کا وقت ختم ہو گیا۔ دوبارہ کوشش کریں۔")
                    time.sleep(1)
                else:
                    st.error("سماعت کا وقت ختم ہو گیا۔ براہ کرم 20 سیکنڈ کے اندر بولیں یا دستی درج کریں۔")
                    text_to_speech_urdu("سماعت کا وقت ختم ہو گیا۔ براہ کرم 20 سیکنڈ کے اندر بولیں۔")
                    return None
            except Exception as e:
                st.error(f"Error in speech-to-text: {e}")
                return None

def capture_photo():
    """Capture a photo using the webcam or upload a photo with validation"""
    st.write("آپ اپنی تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
    captured_image = st.camera_input("ویب کیم سے تصویر لیں")
    if captured_image is not None:
        image = Image.open(captured_image)
        if image.size[0] > 2000 or image.size[1] > 2000:
            st.error("تصویر بہت بڑی ہے۔ براہ کرم 2000x2000 پکسل سے چھوٹی تصویر استعمال کریں۔")
            text_to_speech_urdu("تصویر بہت بڑی ہے۔ براہ کرم چھوٹی تصویر استعمال کریں۔")
            return None
        return np.array(image)

    uploaded_file = st.file_uploader("یا تصویر اپ لوڈ کریں", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        if image.size[0] > 2000 or image.size[1] > 2000:
            st.error("تصویر بہت بڑی ہے۔ براہ کرم 2000x2000 پکسل سے چھوٹی تصویر استعمال کریں۔")
            text_to_speech_urdu("تصویر بہت بڑی ہے۔ براہ کرم چھوٹی تصویر استعمال کریں۔")
            return None
        return np.array(image)

    return None

def convert_urdu_number(urdu_text):
    """Helper function to convert Urdu numbers to integers"""
    if not urdu_text:
        return None
    urdu_to_eng = {
        'ایک': 1, 'دو': 2, 'تین': 3, 'چار': 4, 'پانچ': 5, 'چھ': 6, 'سات': 7, 'آٹھ': 8, 'نو': 9, 'دس': 10,
        'گیارہ': 11, 'بارہ': 12, 'تیرہ': 13, 'چودہ': 14, 'پندرہ': 15, 'سولہ': 16, 'سترہ': 17, 'اٹھارہ': 18,
        'انیس': 19, 'بیس': 20, 'تیس': 30, 'چالیس': 40, 'پچاس': 50, 'ساٹھ': 60
    }
    urdu_text = urdu_text.strip()
    if urdu_text.isdigit():
        return int(urdu_text)
    return urdu_to_eng.get(urdu_text, None)

def ask_question(prompt, step_key, next_step, validate_func=None, error_msg=None, success_msg=None):
    """Helper function to handle voice/manual input for a question"""
    st.write(prompt)
    if st.button("بولیں (Speak)", key=f"speak_{step_key}"):
        response = speech_to_text()
        if response:
            st.write(f"شناخت شدہ جواب: {response}")
            if validate_func:
                validated_response = validate_func(response)
                if validated_response is None:
                    st.error(error_msg)
                    text_to_speech_urdu(error_msg)
                    return
                response = validated_response
            st.session_state.responses[step_key] = response
            if success_msg:
                st.success(success_msg.format(response))
            st.session_state.step = next_step
            return response
    if st.button("دستی درج کریں (Enter Manually)", key=f"manual_{step_key}"):
        if step_key == 'age':
            response = st.number_input("عمر درج کریں", min_value=1, max_value=60, key=f"manual_{step_key}_input")
        else:
            response = st.text_input(f"{prompt} درج کریں", key=f"manual_{step_key}_input")
        if response:
            if validate_func:
                validated_response = validate_func(str(response))
                if validated_response is None:
                    st.error(error_msg)
                    text_to_speech_urdu(error_msg)
                    return
                response = validated_response
            st.session_state.responses[step_key] = response
            if success_msg:
                st.success(success_msg.format(response))
            st.session_state.step = next_step
            return response

def main():
    # Page configuration
    st.set_page_config(page_title="اردو وائس رجسٹریشن فارم", page_icon="🎙️")
    st.title("اردو وائس رجسٹریشن فارم")
    st.subheader("اردو میں رجسٹریشن فارم - وائس ان پٹ کے ساتھ")

    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.responses = {}

    # Step 0: Start
    if st.session_state.step == 0:
        if st.button("شروع کریں (Start)"):
            text_to_speech_urdu("آپ کا نام کیا ہے؟")
            st.session_state.step = 1

    # Step 1: Name
    elif st.session_state.step == 1:
        ask_question("آپ کا نام کیا ہے؟", "name", 2, success_msg="نام محفوظ ہو گیا: {}")
        if st.session_state.step == 2:
            text_to_speech_urdu("آپ کی عمر کیا ہے؟")

    # Step 2: Age
    elif st.session_state.step == 2:
        def validate_age(age_text):
            age = convert_urdu_number(age_text)
            if age is None:
                return None
            if age > 60:
                st.error("معذرت، آپ کی عمر زیادہ ہے")
                text_to_speech_urdu("معذرت، آپ کی عمر زیادہ ہے")
                st.session_state.step = 0
                st.session_state.responses = {}
                return None
            return age

        ask_question("آپ کی عمر کیا ہے؟", "age", 3, validate_age, "عمر سمجھ نہیں آئی۔ براہ کرم دوبارہ کوشش کریں۔", "عمر محفوظ ہو گئی: {}")
        if st.session_state.step == 3:
            text_to_speech_urdu("آپ کی جنس کیا ہے؟")

    # Step 3: Gender
    elif st.session_state.step == 3:
        def validate_gender(gender_text):
            gender_text = gender_text.strip().lower()
            if gender_text in ["مرد", "عورت", "male", "female"]:
                return gender_text
            return None

        ask_question("آپ کی جنس کیا ہے؟ (مرد/عورت)", "gender", 4, validate_gender, "جنس سمجھ نہیں آئی۔ براہ کرم 'مرد' یا 'عورت' بولیں۔", "جنس محفوظ ہو گئی: {}")
        if st.session_state.step == 4:
            text_to_speech_urdu("آپ کے سربراہ کا شناختی کارڈ نمبر کیا ہے؟")

    # Step 4: NIC
    elif st.session_state.step == 4:
        st.write("آپ کے سربراہ کا شناختی کارڈ نمبر کیا ہے؟")
        nic = st.text_input("شناختی کارڈ نمبر درج کریں (13 ہندسوں کا)", key="nic")
        if st.button("اگلا (Next)", key="nic_next_button"):
            if len(nic) == 13 and nic.isdigit():
                st.session_state.responses['nic'] = nic
                st.session_state.step = 5
                text_to_speech_urdu("براہ کرم اپنی تصویر اپ لوڈ کریں یا کیمرے سے تصویر لیں")
            else:
                st.error("براہ کرم درست شناختی کارڈ نمبر درج کریں (13 ہندسوں کا)")
                text_to_speech_urdu("براہ کرم درست شناختی کارڈ نمبر درج کریں")

    # Step 5: Photo
    elif st.session_state.step == 5:
        photo = capture_photo()
        if photo is not None:
            st.image(photo, caption="آپ کی تصویر")
            st.session_state.responses['photo'] = photo
            st.session_state.step = 6

    # Step 6: Submission
    elif st.session_state.step == 6:
        st.success("رجسٹریشن مکمل ہو گئی!")
        text_to_speech_urdu("آپ کی رجسٹریشن مکمل ہو گئی ہے۔ شکریہ")
        st.write("### جمع شدہ معلومات:")
        for key, value in st.session_state.responses.items():
            if key != 'photo':
                st.write(f"{key}: {value}")
        if 'photo' in st.session_state.responses:
            st.image(st.session_state.responses['photo'], caption="جمع شدہ تصویر")

        if st.button("نئی رجسٹریشن (New Registration)"):
            st.session_state.step = 0
            st.session_state.responses = {}

if __name__ == "__main__":
    main()