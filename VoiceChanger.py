# Credit for this mode of this code goes to acrylic, i just changed it a bit
if __name__ == "__main__": # Stops slowdown from recorder starting multiple processes
    from RealtimeSTT import AudioToTextRecorder
    import random
    import string
    import pyautogui
    import os
    import time
    import syllables # I did this because the speech is super inconsistent when based off of character count alone
    import tkinter as tk
    from PIL import ImageTk, Image
    import sys

# TO MAKE IT WORK WITH VB AUDIO CABLE GO TO OPENUTAU PREFERENCES AND SET AUDIO OUTPUT TO VB CABLE IN, AND SET DISCORD AUDIO INPUT TO VB CABLE OUT
# FOR VOSK MAKE SURE YOU HAVE THE MODEL IN THE CORRECT PATH

# - - - Settings - - -
SyllableLength = 250
Debug = 0
StartTone = 67
MinimumTone = 60
ToneFall = 0.5



# - - - Helper Functions - - -
def generate_random_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12)) # I changed the length to 12 and removed the input parameter

def replace_in_file(output_file, replacement_string):
    try:
        words = replacement_string.split()
        Tone = StartTone # Falling tone through a sentence, should be rising for interrogative sentences but that's hard to code
        EndOfSentence = 0 # Flag to reset Tone

        # Open up the template files to create our new ustx file
        with open("Assets\\Template.txt", 'r', encoding='utf-8') as file:
            file_template = file.read()

        with open("Assets\\Word.txt", 'r', encoding='utf-8') as file:
            speech_template = file.read()

        # Creating the ustx file
        updated_content = file_template
        with open(f"Assets\\{output_file}", 'w', encoding='utf-8') as output_file:
            total_dur = 0
            for i in range(len(words)):

                # Changing the position and word for the template to match our text
                segment = speech_template
                segment = segment.replace("POS__", str(total_dur))
                segment = segment.replace("WORD__", words[i])
                Tone -= ToneFall
                Tone = max(Tone, MinimumTone)

                if EndOfSentence:
                    EndOfSentence = 0
                    Tone = StartTone
                
                # Adding small pauses for punctuation and commas
                if any(character in words[i] for character in [".", "?", "!"]):
                    total_dur += SyllableLength
                    EndOfSentence = 1
                if "," in words[i]:
                    total_dur += SyllableLength >> 1 # If syllable length isn't even this is gonna become a float and probably throw an error with OpenUtau
                    EndOfSentence = 1
                
                # Remove characters OpenUtau can't handle
                words[i] = words[i].replace(".","").replace(",","").replace("?","").replace("!","").replace("'","")

                duration = syllables.estimate(words[i])*SyllableLength
                segment = segment.replace("DUR__", str(duration))
                total_dur += duration

                segment = segment.replace("TONE__", str(int(Tone))) # lmfao random.randint(61, 64) is quite a way to get a tone
                
                updated_content = updated_content + "\n" + segment
            
            updated_content = updated_content + "\nwave_parts: []"
            output_file.write(updated_content)

    except Exception as e:
        print(f"An error occurred: {e}")

def play(file):

    if not Debug:

        path = os.path.abspath(f"Assets\\{file}")

        pyautogui.click(x = 1440, y = 540)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(1)
        pyautogui.typewrite(path)
        pyautogui.press('enter')
        time.sleep(1.5)
        pyautogui.press('space')
        os.remove(path)
    
    else:

        print("Done")

def TTS(text):
    output_file = f'{generate_random_string()}.ustx'
    replace_in_file(output_file, text)
    play(output_file)

def MainTetoFunction():
    global SyllableLength, StartTone, MinimumTone

    SyllableLength = int(SyllableLengthEntered.get())
    StartTone = int(StartToneEntered.get())
    MinimumTone = int(MinimumToneEntered.get())

    if not ModeState.get():
        
        for widget in Root.winfo_children():
            widget.destroy()
        tk.Label(Root, text="Wait until this says to speak. RealTimeSTT is initializing.", font=('Arial', 13)).pack(pady=200)
        Root.update()

        recorder = AudioToTextRecorder(language="en")

        while True:
            for widget in Root.winfo_children():
                widget.destroy()
            tk.Label(Root, text="Speak Now, your words will be displayed under this label.", font=('Arial', 13)).pack(pady=200)
            tk.Label(Root, text="Say the word 'Exit' alone if you wish to close the voice changer.", font=("Arial", 11)).pack(pady=100)
            Root.update()

            Text = recorder.text()

            if Text == "Exit.":
                Root.destroy()
                sys.exit(0)

            for widget in Root.winfo_children():
                widget.destroy()
            tk.Label(Root, text="You said:", font=('Arial', 16)).pack(pady=100)
            tk.Label(Root, text=f"{Text}", font=('Arial', 13)).pack(pady=50)
            tk.Label(Root, text="Wait until this says to speak again. Also wait for OpenUtau to finish.").pack(pady=50)
            Root.update()

            output_file = f'{generate_random_string()}.ustx'
            replace_in_file(output_file, Text)
            play(output_file)


    else:
        
        for widget in Root.winfo_children():
            widget.destroy()
        
        Title = tk.Label(Root, text="Teto Voice Changer", font=("Monaco", 30)) # Papyrus wasn't avaliable :(
        Title.pack(pady = 100)

        tk.Label(Root, text="What do you want Teto to say?", font=("Arial", 13)).pack(pady=20)
        Text = tk.Entry(Root)
        Text.pack(pady=50, fill="x")

        tk.Button(Root, text="Speak", font=("Arial", 20), command=lambda: TTS(Text.get())).pack() # I have to use the lambda expression because TTS alone calls the function prematurely, and there's no other way to give the text



# - - - TkInter GUI - - -
if __name__ == "__main__": # The recorder restarts python so i gotta make it not create more guis
    Root = tk.Tk()
    Root.title("Teto Voice Changer")
    Root.geometry("600x800")

    Title = tk.Label(Root, text="Teto Voice Changer", font=("Monaco", 30)) # Papyrus wasn't avaliable :(
    Title.pack(pady = 20)

    Frame = tk.Frame(Root)
    Frame.pack(pady=10)

    tk.Label(Frame, text="Check this for Text to Teto, leave unchecked for Speech to Teto", font=("Arial", 13)).grid(row=0, column=0)
    ModeState = tk.BooleanVar()
    ModeEntered = tk.Checkbutton(Frame, variable=ModeState)
    ModeEntered.grid(row=0, column=1, pady=10)

    tk.Label(Frame, text="How long should each syllable be in milliseconds? (250 is good)", font=("Arial", 13)).grid(row=1, column=0)
    SyllableLengthEntered = tk.Entry(Frame)
    SyllableLengthEntered.grid(row=1, column=1, pady=10)

    tk.Label(Frame, text="What tone should Teto start with? (67-70 is good)", font=("Arial", 13)).grid(row=2, column=0)
    StartToneEntered = tk.Entry(Frame)
    StartToneEntered.grid(row=2, column=1, pady=10)

    tk.Label(Frame, text="What tone should Teto go down to? (60-63 is good)", font=("Arial", 13)).grid(row=3, column=0)
    MinimumToneEntered = tk.Entry(Frame)
    MinimumToneEntered.grid(row=3, column=1, pady=10)

    tk.Button(Root, text="Start the Voice Changer", font=("Arial", 20), command=MainTetoFunction).pack(pady=100)

    tk.Label(Root, text="Set up your OpenUtau window like this vvvvvvvvv", font=('Arial', 13)).pack()
    ExampleImage = Image.open("Assets\\Example.png")
    ExampleImage = ExampleImage.resize((384, 216), resample=Image.Resampling.BICUBIC)
    ExampleImage = ImageTk.PhotoImage(ExampleImage)
    tk.Label(Root, image=ExampleImage).pack(pady=20)

    Root.mainloop()
