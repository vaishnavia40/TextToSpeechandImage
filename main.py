import requests
import speech_recognition as sr
from rake_nltk import Rake
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView

# Replace with your actual API key
API_KEY = 'AIzaSyAjwvDJmEdbWhrzWR-17OctIS0ib4zfneU'
# Replace with your actual Custom Search Engine ID
SEARCH_ENGINE_KEY = '7564b8c73e277468a'

class SpeechToTextApp(MDApp):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)

        self.transcription_label = MDLabel(text="Transcription:", halign='center')
        self.keywords_label = MDLabel(text="Extracted Keywords:", halign='center')
        self.image_results_label = MDLabel(text="Image Search Results:", halign='center')

        start_button = MDRaisedButton(text="Start Speech to Text")
        start_button.bind(on_press=self.start_speech_to_text)

        self.image_grid = MDGridLayout(cols=2, spacing=10, size_hint_y=None)
        self.image_scrollview = ScrollView()

        self.image_grid.bind(minimum_height=self.image_grid.setter('height'))
        self.image_scrollview.add_widget(self.image_grid)

        layout.add_widget(self.transcription_label)
        layout.add_widget(self.keywords_label)
        layout.add_widget(self.image_results_label)
        layout.add_widget(start_button)
        layout.add_widget(self.image_scrollview)

        return layout

    def start_speech_to_text(self, instance):
        self.image_grid.clear_widgets()  # Clear previous images
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening... Speak into the microphone")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                self.transcription_label.text = f"Transcription: {text}"
                keywords = self.extract_keywords(text)
                self.keywords_label.text = f"Extracted Keywords: {', '.join(keywords)}"
                self.search_images(keywords)
            except sr.UnknownValueError:
                print("Speech not recognized")
            except sr.RequestError as e:
                print(f"Could not request results: {e}")

    def extract_keywords(self, text):
        r = Rake()
        r.extract_keywords_from_text(text)
        keywords_with_scores = r.get_ranked_phrases_with_scores()
        return [keyword for score, keyword in keywords_with_scores if score > 5]

    def search_images(self, keywords):
        search_query = ' '.join(keywords)
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': search_query,
            'key': API_KEY,
            'cx': SEARCH_ENGINE_KEY,
            'searchType': 'image'
        }
        response = requests.get(url, params=params)
        results = response.json().get('items', [])
        for result in results[:10]:  # Display up to 10 images
            image = AsyncImage(source=result['link'], size_hint_y=None, height=300)
            self.image_grid.add_widget(image)

if __name__ == "__main__":
    SpeechToTextApp().run()