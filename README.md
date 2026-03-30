# Voice Assistant using Python
#This project is a voice assistant that can open apps, search Google, and speak responses.
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import pywhatkit

# Initialize engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("Window:", text)
    engine.say(text)
    engine.runAndWait()

def take_command():
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        listener.adjust_for_ambient_noise(source)
        audio = listener.listen(source)

    try:
        command = listener.recognize_google(audio)
        command = command.lower()
        print("You:", command)
        return command
    except Exception as e:
        print("Error:", e)
        speak("I didn't get that, can you repeat?")
        return ""

def run_window():
    speak("Hello, I am Window. How can I help you?")

    while True:
        command = take_command()
        
        if command == "":
           speak("I didn't get that, can you repeat?")
           continue

        if "time" in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            speak("Current time is " + time)

        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            speak("Opening Google")

        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")

        elif "open Brave" in command:
            webbrowser.open("https://brave.com/")
            speak("Opening Brave")  

        elif "search" in command:
            command = command.replace("search", "")
            pywhatkit.search(command)
            speak("Searching for " + command)

        elif "who is" in command:
            person = command.replace("who is", "")
            try:
               info = wikipedia.summary(person, 1)
               speak(info)
            except:
                 speak("Sorry, I couldn't find information.")
            
        elif "play" in command:
           song = command.replace("play", "")
           pywhatkit.playonyt(song)
           speak("Playing " + song) 
              
        elif "open notepad" in command:
            os.system("notepad")
            speak("Opening Notepad")

        elif "stop" in command or "exit" in command:
            speak("Goodbye")
            break

        else:
            speak("I didn't get that, can you repeat?")
        
run_window()
