# vernacular_simple.py
import os
import tempfile
import google.generativeai as genai
from gtts import gTTS
from playsound import playsound

class SimpleVoiceAssistant:
    def __init__(self, api_key=None):
        """Simple voice assistant without speech_recognition"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ Please set GEMINI_API_KEY environment variable")
            print("Run: set GEMINI_API_KEY=your_api_key_here")
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def text_to_speech(self, text, language='te'):
        """Convert text to speech"""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                temp_path = f.name
            tts.save(temp_path)
            playsound(temp_path)
            os.unlink(temp_path)
        except Exception as e:
            print(f"Audio error: {e}")
    
    def chat(self):
        """Simple text-based chat with voice output"""
        print("🏪 MSME Voice Assistant (Text Mode)")
        print("Type 'exit' to quit\n")
        
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Determine language
            if any('\u0c00' <= char <= '\u0c7f' for char in user_input[:10]):
                lang = 'te'
                prompt = f"Respond in Telugu to: {user_input}"
            elif any('\u0900' <= char <= '\u097f' for char in user_input[:10]):
                lang = 'hi'
                prompt = f"Respond in Hindi to: {user_input}"
            else:
                lang = 'en'
                prompt = f"Respond in English to: {user_input}"
            
            try:
                response = self.model.generate_content(prompt)
                print(f"Assistant: {response.text}")
                
                # Play audio
                self.text_to_speech(response.text, lang)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    assistant = SimpleVoiceAssistant()
    assistant.chat()
