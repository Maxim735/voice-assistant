import string
import speech_recognition
import wikipedia
import pyttsx3
import joblib
import webbrowser
import traceback

from PyQt5.QtWidgets import QMessageBox


class Assistant:
    ttsEngine = None
    voices = None
    name = None
    talk_model = None

    def __init__(self):
        # initialization of the speech synthesis tool
        self.ttsEngine = pyttsx3.init()

        # loading a neural model from disk
        self.talk_model = joblib.load(r'mmm_just_Alice.pkl')
        self.voices = self.ttsEngine.getProperty("voices")
        name = "Blonde"
        # Microsoft Kira Desktop - Eng(USA)
        self.ttsEngine.recognition_lang = "ru-RU"
        self.ttsEngine.setProperty("voice", self.voices[0].id)

    def play_voice_assistant_speech(self, text):
        # voice assistant response speech playback
        self.ttsEngine.say(str(text))
        self.ttsEngine.runAndWait()

    def video_search(self, *args: tuple):
        """
        search for a query on YouTube and open a link with answers to the query
        :param args: search term
        """
        if not args[0]:
            return
        search_term = ''.join(args[0])
        url = "https://www.youtube.com/results?search_query=" + search_term
        webbrowser.get().open(url)
        return "Вот, что я нашла по " + search_term + "на youtube"

    def wiki_search(self, *args: tuple):
        """
        Search in Wikipedia, followed by voicing the results and opening links
        :param args: search term
        """
        if not args[0]:
            return

        search_term = ''.join(args[0])

        wiki_page = wikipedia.page(search_term)

        try:
            if wiki_page.url != "":

                webbrowser.get().open(wiki_page.url)

                # чтение ассистентом первых двух предложений summary со страницы Wikipedia
                # (могут быть проблемы с мультиязычностью)

                return "Вот, что я нашла по " + search_term + " на Wikipedia: "
            else:
                # открытие ссылки на поисковик в браузере в случае, если на Wikipedia не удалось найти ничего по запросу
                self.play_voice_assistant_speech("Не могу найти " + search_term + "на Wikipedia. /"
                                                                               "Но вот, что я нашла в гугле")
                url = "https://google.com/search?q=" + search_term
                webbrowser.get().open(url)

                return "Ну могу найти " + search_term + "на Wikipedia. /" "Но вот, что я нашла в гугле"
        except():
            self.play_voice_assistant_speech("Seems like we have a trouble. See logs for more information")
            traceback.print_exc()
            return "Seems like we have a trouble. See logs for more information"

    # function which gives an answer (string) on the message (string)
    def answer(self, user_input_str):
        # a function that loads user input into the neural model and predicts the response
        if user_input_str.find("найди в википедии") != -1:
            return self.wiki_search(user_input_str[17:])
        elif user_input_str.find("найди на ютубе") != -1:
            return self.video_search(user_input_str[15:])
        else:
            answer = self.talk_model.predict([user_input_str])[0]
            return answer


def record_and_recognize_audio():
    with speech_recognition.Microphone(device_index=0) as source:
        r = speech_recognition.Recognizer()
        print("Speak...")

        try:
            audio = r.listen(source=source, phrase_time_limit=5, timeout=7)
            query = r.recognize_google(audio, language='ru-RU')

        except(speech_recognition.WaitTimeoutError, speech_recognition.UnknownValueError):
            msg_box = QMessageBox()
            msg_box.setText("Error! Check your micro!")
            msg_box.exec()
            print("Error!")

        else:
            return query.capitalize()


def cleaner(x):
    """
    cleaning function required for neural model
    """
    return [a for a in (''.join([a for a in x if a not in string.punctuation])).lower().split()]