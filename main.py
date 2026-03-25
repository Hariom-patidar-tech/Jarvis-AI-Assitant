import os
import requests
import webbrowser
import wikipedia
import pyjokes
import pyttsx3
import speech_recognition as sr
from google import genai
import musicLibrary

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
print("NEWS KEY:", NEWS_API_KEY)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
print("WEATHER KEY:", WEATHER_API_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Gemini Key:", os.getenv("GEMINI_API_KEY"))

client = genai.Client(api_key=GEMINI_API_KEY)
recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    if "David" in voice.name:   
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 160)   
engine.setProperty('volume', 1.0)

def speak(text: str):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Speech Error:", e)

def aiProcess(command: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"You are Jarvis. Reply short. {command}"
        )
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, AI error"

def get_weather(city: str) -> str:
    """Fetch live weather data for a city."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"The current temperature in {city} is {temp}°C with {condition}."
    except Exception as e:
        print("Weather API Error:", e)
        return "Sorry, I couldn't fetch the weather right now."

def processCommand(c: str):
    """Process user voice command and perform action."""
    c_lower = c.lower().strip()

    if "open google" in c_lower:
        webbrowser.open("https://google.com")
    elif "open facebook" in c_lower:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c_lower:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c_lower:
        webbrowser.open("https://linkedin.com")

    elif c_lower.startswith("play"):
        song = c_lower.replace("play", "").strip()
        if song in [key.lower() for key in musicLibrary.music]:
            for key, link in musicLibrary.music.items():
                if key.lower() == song:
                    webbrowser.open(link)
                    speak(f"Playing {key}")
                    break
        else:
            speak(f"Sorry, I don't have {song}. Searching on YouTube...")
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={song}")

    elif "news" in c_lower:
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}")
            r.raise_for_status()
            data = r.json()
            articles = data.get("articles", [])
            if not articles:
                speak("Sorry, I couldn't find any news right now.")
            else:
                speak("Here are the top 5 headlines.")
                for article in articles[:5]:
                    speak(article.get("title", ""))
        except Exception as e:
            print("News API Error:", e)
            speak("Sorry, I am unable to fetch news at the moment.")

    elif "weather in" in c_lower:
        city = c_lower.split("weather in")[-1].strip()
        report = get_weather(city)
        speak(report)

    elif any(op in c_lower for op in ["plus", "minus", "times", "multiplied", "divided", "/", "+", "-", "*"]):
        try:
            expression = c_lower.replace("plus", "+").replace("minus", "-")\
                                .replace("times", "*").replace("multiplied", "*")\
                                .replace("divided", "/").replace("by", "")
            result = eval(expression)
            speak(f"The answer is {result}")
        except:
            speak("Sorry, I couldn't calculate that.")

    elif "tell me about" in c_lower:
        topic = c_lower.replace("tell me about", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary)
        except:
            speak("Sorry, I couldn't find information on that topic.")

    elif "joke" in c_lower:
        joke = pyjokes.get_joke()
        speak(joke)

    else:
        output = aiProcess(c)
        speak(output)

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for wake word...")
                audio = recognizer.listen(
                    source, timeout=10, phrase_time_limit=5)

            word = recognizer.recognize_google(audio)
            print("Heard:", word)

            if "jarvis" in word.lower():
                speak("Yes, how can I help you?")
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("Jarvis Active... Listening for command")
                    audio = recognizer.listen(
                        source, timeout=10, phrase_time_limit=8)
                    command = recognizer.recognize_google(audio)
                    print("Command:", command)
                    processCommand(command)

        except Exception as e:
            print("Error:", e)