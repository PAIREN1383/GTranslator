from googletrans import Translator
from tkinter import messagebox
from tkinter import font
from tkinter import *
from keyboard import add_hotkey
from time import sleep
from gtts import gTTS, gTTSError # Install gTTS.
from pyttsx3 import init # Install pyttsx3.
from playsound import playsound #HINT: Install playsound version 1.2.2
from os import remove


########################## Front-End ##########################
window = Tk()
window.title("GTranslator")
window.geometry("350x350")
icon = PhotoImage(file=".\\gt_icon.png")
window.call("wm", "iconphoto", window._w, icon)
entxt_font = font.Font(family="tahoma", size=10, weight="bold")
fatxt_font = font.Font(family="Vazir", size=10, weight="bold")
sp_font = font.Font(family="Segoe UI", size=10)


def help_box():
    messagebox.showinfo("GTranslator", "You can use the translator in two ways:\n \
                        \n[1] Select the word or sentence and press 'Ctrl+C'. \
                        \n[2] Enter the word or sentence in the entry and press 'Enter' or click the Translate button. \
                        \n\n\nPublisher: MohammadAli \
                        \nGitHub: https://github.com/pairen1383/ \
                        \nVersion: 1.0.1")


def show_searchbar():
    global ent
    lb = Label(window, justify="left", text="Text: ")
    lb.place(x=0, y=2)

    raw_text = StringVar()
    ent = Entry(window, justify="left", textvariable=raw_text, width=31)
    ent.place(x=32, y=4)

    vbtn = Button(window, text=u"\U0001F50A", width=2, height=1, command=play_voice, font=sp_font)
    vbtn.place(x=224, y=0)

    tbtn = Button(window, text="Translate", width=8, command=ent_key)
    tbtn.place(x=250, y=2)

    hbtn = Button(window, text="?", width=2, command=help_box)
    hbtn.place(x=325, y=0)


# We clear the window so that there is no text on the page that goes under another text.
def clear_window():
    for widget in window.winfo_children():
        widget.destroy()


########################## Back-End ##########################
# Persian text is written from right to left.
def justify_txt(tr_text, in_text, zoom, extra=[]):
    global ent, trtxt
    clear_window()
    show_searchbar()
    ent.delete(0, END) # Clear the entry.
    ent.insert(0, in_text) # Displays the entered text.
    trtxt = Text(window, width=46, height=3, font=fatxt_font, wrap=WORD)
    sc1 = Scrollbar(window)
    sc1.place(x=330, y=35)
    sc1.config(command=trtxt.yview)
    trtxt.delete("1.0", END) # Clear the Textarea.
    trtxt.tag_configure("rt", justify="right") # Persian text is written from right to left.
    trtxt.insert(INSERT, tr_text)
    trtxt.tag_add("rt", 1.0, "end") # Add tag from beginning (Line 1 and index 0) to end.
    trtxt.place(x=2, y=35)

    if extra != []:
        trlb = Label(window, justify="left", text="Other translations:")
        trlb.place(x=0, y=105)
        other_trtxt = Text(window, width=46, height=3, font=fatxt_font, wrap=WORD)
        sc2 = Scrollbar(window)
        sc2.place(x=330, y=125)
        sc2.config(command=other_trtxt.yview)
        other_trtxt.delete("1.0", END)
        for obj in extra[0]:
            obj.replace("{", "").replace("}", "") # Remove unwanted characters.
            obj.strip()
        other_trtxt.tag_configure("rt", justify="right")
        other_trtxt.insert(INSERT, " ،".join(extra[0])) # Separate it.
        other_trtxt.tag_add("rt", 1.0, "end")
        other_trtxt.place(x=2, y=125)

        inlb1 = Label(window, justify="left", text="Synonyms:")
        inlb1.place(x=0, y=195)
        intxt = Text(window, width=40, height=3, font=entxt_font, wrap=WORD)
        sc3 = Scrollbar(window)
        sc3.place(x=330, y=215)
        sc3.config(command=intxt.yview)
        intxt.delete("1.0", END)
        intxt.insert("1.0", ", ".join(extra[1]))
        intxt.place(x=2, y=215)

        inlb2 = Label(window, justify="left", text="Definition:")
        inlb2.place(x=0, y=270)
        other_intxt = Text(window, width=40, height=3, font=entxt_font, wrap=WORD)
        sc4 = Scrollbar(window)
        sc4.place(x=330, y=290)
        sc4.config(command=other_intxt.yview)
        other_intxt.delete("1.0", END)
        other_intxt.insert("1.0", extra[2])
        other_intxt.place(x=2, y=290)
        ent.delete(0, END)
        ent.insert(0, in_text)

    if zoom: # Appears when the program is minimized or placed under other windows.
        window.attributes("-topmost", True)
        window.state("normal")
        window.attributes("-topmost", False) # Do not delete this line because the program will never go under another window.


def translate_txt(txt, show_win=False):
    translator = Translator()
    flag = False
    try:
        res = translator.translate(text=txt, src="en", dest="fa")
        try:
            extra_dt = [res.extra_data['all-translations'][0][1],
                    res.extra_data['all-translations'][0][2][0][1],
                    res.extra_data['definitions'][0][1][0][0]]
        except:
            flag = True
            justify_txt(res.text, txt, show_win)
        if flag == False: # 2 Translation is prohibited.
            justify_txt(res.text, txt, show_win, extra_dt)
    except TypeError: # Entry is empty.
        messagebox.showerror("GTranslator", "Error: \nEnter a sentence or word!")
    except Exception as err:
        if str(err) == "[Errno 11001] getaddrinfo failed": # User is offline.
            messagebox.showerror("GTranslator", "Error: \nPlease connect to the Internet.")
        else: # Another error.
            messagebox.showerror("GTranslator", f"Error: \n{err}")


def play_voice():
    global ent
    get_txt = ent.get().strip() # Delete unwanted spaces after and before the text or word.
    if get_txt == "":
        messagebox.showerror("GTranslator", "Error: \nEnter a sentence or word!")
        return None
    try:
        tts = gTTS(get_txt, timeout=3)
        tts.save(".\\never_save.mp3")
        playsound(".\\never_save.mp3")
        remove(".\\never_save.mp3")
    except gTTSError: # User is offline.
        remove(".\\never_save.mp3") # The corrupted file has not been deleted.
        # This is an offline voice maker.
        engine = init()
        engine.setProperty("rate", 120) # Text or word reading speed.
        engine.say(get_txt)
        engine.runAndWait()
    except Exception as err: # Always be careful.
        messagebox.showerror("GTranslator", f"Error: \n{err}")


# Ctrl+C handler.
def clip_key():
    sleep(0.2) # The text must be saved to the clipboard.
    try:
        selected_text = window.clipboard_get()
        translate_txt(selected_text, True)
    except TclError: # Clipboard is empty.
        messagebox.showerror("GTranslator", "Error: \nCopy a sentence or word!")
    except Exception as err: # Always be careful.
        messagebox.showerror("GTranslator", f"Error: \n{err}")


# Get the word or text from the entry by pressing "Enter" or clicking the "Translate" button.
def ent_key():
    global ent
    translate_txt(ent.get().strip())


add_hotkey("ctrl+c", clip_key)
add_hotkey("enter", ent_key)


########################## Start ##########################
show_searchbar()
window.mainloop()
