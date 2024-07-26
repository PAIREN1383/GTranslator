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
window.geometry("350x400")
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
                        \nVersion: 2.1.2")


def show_searchbar():
    global ent, on_off

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

    on_off = BooleanVar()
    checkbox = Checkbutton(window, variable=on_off, onvalue=True, offvalue=False)
    checkbox.place(x=2, y=23)

    cblb = Label(window, justify="left", text="Always use offline pronunciation.")
    cblb.place(x=20, y=25)


class Label_Text_area:
    def __init__(self, wid_root, lb_x, lb_y, lb_txt, lb_justify, ta_scrollbar_x_margin, ta_width, ta_height, ta_font, ta_data, ta_justify) -> None:
        self.root = wid_root
        self.lb_x = lb_x
        self.lb_y = lb_y
        self.lb_txt = lb_txt
        self.lb_justify = lb_justify
        self.margin = ta_scrollbar_x_margin
        self.ta_width = ta_width
        self.ta_height = ta_height
        self.ta_font = ta_font
        self.ta_justify = ta_justify
        self.ta_data = ta_data

        if self.lb_txt != "":
            txt_lb = Label(self.root, justify=self.lb_justify, text=self.lb_txt)
            txt_lb.place(x=self.lb_x, y=self.lb_y)
        self.txt_area = Text(self.root, width=self.ta_width, height=self.ta_height, font=self.ta_font, wrap=WORD)
        self.sc = Scrollbar(self.root)
        self.sc.place(x=self.lb_x + self.margin + self.ta_width * 8, y=self.lb_y + 20) # Approximately 1 unit of width equals 8 units of x-position
        self.sc.config(command=self.txt_area.yview)
        self.txt_area.tag_configure("tg_name", justify=self.ta_justify) # Persian text is written from right to left.
        self.txt_area.insert(INSERT, self.ta_data)
        self.txt_area.tag_add("tg_name", 1.0, "end") # Add tag from beginning (Line 1 and index 0) to end.
        self.txt_area.place(x=self.lb_x, y=self.lb_y + 20) # The text area and scroll bar should be 20 y-position down.

    def update_ta(self, new_data):
        self.ta_data = new_data
        self.txt_area.delete("1.0", END) # Clear the Textarea.
        self.txt_area.insert(INSERT, self.ta_data)
        self.txt_area.tag_add("tg_name", 1.0, "end") # It must be applied every time.


def basic_view():
    global trtxt, other_trtxt, intxt, other_intxt
    show_searchbar()
    trtxt = Label_Text_area(window, 2, 50, "Translated text:", "left", -40, 46, 3, fatxt_font, "", "right")
    other_trtxt = Label_Text_area(window, 2, 145, "Other translations:", "left", -40, 46, 3, fatxt_font, "", "right")
    intxt = Label_Text_area(window, 2, 240, "Synonyms:", "left", 8, 40, 3, entxt_font, "", "left")
    other_intxt = Label_Text_area(window, 2, 320, "Definition:", "left", 8, 40, 3, entxt_font, "", "left")


# Persian text is written from right to left.
def justify_txt(tr_text, in_text, zoom, extra=[]):
    global ent, trtxt, other_trtxt, intxt, other_intxt
    ent.delete(0, END) # Clear the entry.
    ent.insert(0, in_text) # Displays the entered text.
    trtxt.update_ta(tr_text)
    if extra != []:
        for obj in extra[0]:
            obj.replace("{", "").replace("}", "") # Remove unwanted characters.
            obj.strip()
        other_trtxt.update_ta(" ،".join(extra[0]))
        intxt.update_ta(", ".join(extra[1]))
        other_intxt.update_ta(extra[2])
    else:
        other_trtxt.update_ta("")
        intxt.update_ta("")
        other_intxt.update_ta("")

    if zoom: # Appears when the program is minimized or placed under other windows.
        window.attributes("-topmost", True)
        window.state("normal")
        window.attributes("-topmost", False) # Do not delete this line because the program will never go under another window.


########################## Back-End ##########################
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
    global ent, on_off
    get_txt = ent.get().strip() # Delete unwanted spaces after and before the text or word.
    if get_txt == "":
        messagebox.showerror("GTranslator", "Error: \nEnter a sentence or word!")
        return None
    if on_off.get():
        play_voice_offline(get_txt)
    else:
        play_voice_online(get_txt)


def play_voice_online(get_txt):
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


def play_voice_offline(get_txt):
    # This is an offline voice maker.
    engine = init()
    engine.setProperty("rate", 120) # Text or word reading speed.
    engine.say(get_txt)
    engine.runAndWait()


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


########################## Start ##########################
add_hotkey("ctrl+c", clip_key)
add_hotkey("enter", ent_key)
basic_view()
window.mainloop()
