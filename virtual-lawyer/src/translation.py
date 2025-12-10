from googletrans import Translator
import langdetect

class LanguageHandler:
    def __init__(self):
        self.translator = Translator()
    
    def detect_language(self, text):
        """Detect if text is Urdu or English"""
        try:
            lang = langdetect.detect(text)
            return 'ur' if lang == 'ur' else 'en'
        except:
            return 'en'
    
    def translate_to_english(self, urdu_text):
        """Translate Urdu to English"""
        try:
            result = self.translator.translate(urdu_text, src='ur', dest='en')
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return urdu_text
    
    def translate_to_urdu(self, english_text):
        """Translate English to Urdu"""
        try:
            result = self.translator.translate(english_text, src='en', dest='ur')
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return english_text
    
    def process_query(self, query):
        """Process query: detect language and translate if needed"""
        lang = self.detect_language(query)
        
        if lang == 'ur':
            english_query = self.translate_to_english(query)
            return {
                'original': query,
                'english': english_query,
                'language': 'ur',
                'needs_translation_back': True
            }
        else:
            return {
                'original': query,
                'english': query,
                'language': 'en',
                'needs_translation_back': False
            }