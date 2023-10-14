"""
Required imports
"""
import subprocess
import os
import sys
import time
import functools
from tkinter import filedialog
from configparser import ConfigParser
import ttkbootstrap as ttkb
from PIL import Image, ImageGrab, UnidentifiedImageError
import pytesseract
from pytesseract import TesseractError


class DefaultValues:
    """
    Class for the language entity - Done to avoid a global variable
    """

    def __init__(self):
        try:
            self.language = config.get("Settings", "lang")
            self.long_name = config.get("Settings", "long_name")
            self.theme = config.get("Settings", "theme")
        except config.Error: #pylint: disable=no-member
            self.language = "eng"
            self.long_name = "English"
            self.theme = "pulse"

    def __str__(self):
        return self.language

    def print_name(self):
        """Returns the long form name"""
        return self.long_name


# Checks for the Tesseract exe, if not found opens a file window

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
if not os.path.exists(TESSERACT_PATH):
    while True:
        TESSERACT_PATH = filedialog.askopenfilename(
            title="Select Tesseract Executable",
            filetypes=[("Executable files", "*.exe")],
        )
        if not TESSERACT_PATH:
            sys.exit()
        if os.path.basename(TESSERACT_PATH) != "tesseract.exe":
            continue
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        break

# Takes the location of the exe and saves the relative tessdate folder

LOCALES_PATH = TESSERACT_PATH.split("tesseract.exe")
LOCALES_PATH = LOCALES_PATH[0] + "tessdata"
FILES = os.listdir(LOCALES_PATH)

# Reads the config.ini or creates it it doesn't exist

CONFIG_FILE = "config.ini"
config = ConfigParser()
if not os.path.exists(CONFIG_FILE):
    # Set default values
    config["Settings"] = {"theme": "pulse", "lang": "eng", "long_name": "English"}
    # Write the configuration to the file
    try:
        with open(CONFIG_FILE, "w", encoding="UTF-8") as configfile:
            config.write(configfile)
    except IOError:
        pass

# Read values from the configuration file
try:
    config.read(CONFIG_FILE)
except config.Error: #pylint: disable=no-member
    print("Error in config file")
LANG = DefaultValues()

# ============== LANGUAGE =================


def check_languages(language_menu, language_display):
    """
    Checks the OCR training data exists in the tesdate folder
    if it does, it creates an option in the menu
    """
    found_file = False
    for lang_code, lang_name in languages.items():
        for file in FILES:
            if file.startswith(lang_code):
                found_file = True
                break
        if found_file:
            partial_lang_code = functools.partial(
                set_language, lang_code, lang_name, language_display
            )
            language_menu.add_command(label=lang_name, command=partial_lang_code)
            found_file = False


def set_language(language, long_name, language_display):
    """
    Set the language
    """
    LANG.language = language
    LANG.long_name = long_name
    language_display.config(text=f"Language: {LANG.long_name}")


# ============== INTERFACE =================


def dark_mode(root):
    """
    Set the dark mode theme for the tkinter application.
    Args:
        root (tk.Tk): The tkinter root window.
        menu (function): The menu function to be called after setting the dark mode theme.
    Returns:
        None
    """
    LANG.theme = "darkly"
    root.style.theme_use("darkly")


def light_mode(root):
    """
    Set the light mode theme for the tkinter application.
    Args:
        root (tk.Tk): The tkinter root window.
        menu (function): The menu function to be called after setting the light mode theme.
    Returns:
        None
    """
    LANG.theme = "pulse"
    root.style.theme_use("pulse")


# ============== CONVERSION =================


def convert_image_to_text(image_path):
    """
    Convert an image to text using Tesseract OCR.
    Args:
        image_path (str): The file path to the input image.

    Returns:
        str: The extracted text from the image.
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=LANG.language)
        return text
    except pytesseract.pytesseract.TesseractNotFoundError:
        return "Error: Tesseract OCR failed to process the image"


def open_from_clipboard(text_display, root):
    """
    Open an image from the clipboard and extract text using Tesseract OCR.
    Args:
        text_display (tk.Text): The tkinter Text widget to display the extracted text.
        root (tk.Tk): The tkinter root window.
    Returns:
        None
    """
    clear_text(text_display)
    try:
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image is not None:
            text = pytesseract.image_to_string(clipboard_image, lang=LANG.language)
            update_text(text_display, root, text)
        else:
            update_text(text_display, root, "No image in clipboard")
    except AttributeError:
        update_text(text_display, root, "Error: Unable to access clipboard or image")
    except TesseractError:
        update_text(
            text_display, root, "Error: Tesseract OCR failed to process the image"
        )


def open_image_dialog(text_display, root):
    """
    Open a file dialog to select an image file, extract text
    from the image, and display it in the tkinter Text widget.
    Args:
        text_display (tk.Text): The tkinter Text widget to display the extracted text.
        root (tk.Tk): The tkinter root window.
    Returns:
        None
    """
    try:
        text = ""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff")]
        )
        if file_path:
            clear_text(text_display)
            text = convert_image_to_text(file_path)
        update_text(text_display, root, text)
    except UnidentifiedImageError:
        update_text(text_display, root, "Error: Unable to identify image")


def capture_screen(text_display, root):
    """
    Opens Snips & clip! and minimizes the window when the capture button is clicked
    """
    try:
        root.state(newstate="iconic")
        command = "explorer ms-screenclip:"
        subprocess.run(command, shell=True, check=False)
    except subprocess.CalledProcessError:
        return
    root.bind("<Enter>", lambda event: on_enter(text_display, root))
    time.sleep(1)
    root.state(newstate="normal")


def save_as(text_display):
    """
    Save the contents of the text_display to a file.
    Args:
        text_display (tk.Text): The tkinter Text widget containing the text to be saved.
    Returns:
        None
    """
    text = text_display.get(1.0, ttkb.END)
    file_path = filedialog.asksaveasfilename(
        initialfile="converted.txt", filetypes=[("Text files", "*.txt")]
    )
    if not file_path.endswith(".txt"):
        file_path += ".txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)


# ============== UTILITY =================


def on_closing(root):
    """Closes the application and saves changes if there were any"""
    try:
        config["Settings"] = {
            "theme": f"{LANG.theme}",
            "lang": f"{LANG.language}",
            "long_name": f"{LANG.long_name}",
        }

        with open(CONFIG_FILE, "w", encoding="UTF-8") as config_file_b:
            config.write(config_file_b)
    except config.Error: #pylint: disable=no-member
        pass
    root.destroy()


def clear_text(text_display):
    """
    Clear the text displayed in the tkinter Text widget.
    Args:
        text_display (tk.Text): The tkinter Text widget to be cleared.
    Returns:
        None
    """
    text_display.delete(1.0, ttkb.END)


def copy_all(text_display, root):
    """
    Copy all text from the tkinter Text widget to the clipboard.
    Args:
        text_display (tk.Text): The tkinter Text widget containing the text to be copied.
        root (tk.Tk): The tkinter root window.
    Returns:
        None
    """
    root.clipboard_clear()
    root.clipboard_append(text_display.get(1.0, ttkb.END))


def update_text(text_display, root, text):
    """
    Update the text displayed in the tkinter Text widget and bind a context menu to it.
    Args:
        text_display (tk.Text): The tkinter Text widget to display the text.
        root (tk.Tk): The tkinter root window.
        text (str): The text to be displayed in the Text widget.
    Returns:
        None
    """
    text_display.insert(ttkb.END, text)
    context_menu = ttkb.Menu(root, tearoff=0)
    context_menu.add_command(
        label="Copy",
        command=lambda: root.clipboard_clear()
        or root.clipboard_append(text_display.get("sel.first", "sel.last")),
    )
    context_menu.add_separator()
    context_menu.add_command(
        label="Cut",
        command=lambda: root.clipboard_clear()
        or root.clipboard_append(text_display.get("sel.first", "sel.last"))
        or text_display.delete("sel.first", "sel.last"),
    )
    context_menu.add_separator()
    context_menu.add_command(
        label="Paste",
        command=lambda: text_display.insert(ttkb.INSERT, root.clipboard_get()),
    )
    text_display.bind(
        "<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root)
    )


def on_enter(text_display, root):
    """
    When the users goes back to the root window the captured image is pasted
    """
    open_from_clipboard(text_display, root)
    return root.unbind("<Enter>")


languages = {
    "afr": "Afrikaans",
    "amh": "Amharic",
    "ara": "Arabic",
    "asm": "Assamese",
    "aze": "Azerbaijani",
    "aze_cyrl": "Azerbaijani",
    "bel": "Belarusian",
    "ben": "Bengali",
    "bod": "Tibetan",
    "bos": "Bosnian",
    "bre": "Breton",
    "bul": "Bulgarian",
    "cat": "Catalan; Valencian",
    "ceb": "Cebuano",
    "ces": "Czech",
    "chi_sim": "Chinese - Simplified",
    "chi_tra": "Chinese - Traditional",
    "chr": "Cherokee",
    "cym": "Welsh",
    "dan": "Danish",
    "deu": "German",
    "dzo": "Dzongkha",
    "ell": "Greek, Modern",
    "eng": "English",
    "enm": "English, Middle (1100-1500)",
    "epo": "Esperanto",
    "equ": "Math / equation detection module",
    "est": "Estonian",
    "eus": "Basque",
    "fas": "Persian",
    "fin": "Finnish",
    "fra": "French",
    "frm": "French, Middle (ca.1400-1600)",
    "gle": "Irish",
    "glg": "Galician",
    "guj": "Gujarati",
    "hat": "Haitian; Haitian Creole",
    "heb": "Hebrew",
    "hin": "Hindi",
    "hrv": "Croatian",
    "hun": "Hungarian",
    "iku": "Inuktitut",
    "ind": "Indonesian",
    "isl": "Icelandic",
    "ita": "Italian",
    "jav": "Javanese",
    "jpn": "Japanese",
    "kan": "Kannada",
    "kat": "Georgian",
    "kaz": "Kazakh",
    "khm": "Central Khmer",
    "kir": "Kirghiz; Kyrgyz",
    "kor": "Korean",
    "kur": "Kurdish (Arabic Script)",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "mal": "Malayalam",
    "mar": "Marathi",
    "mkd": "Macedonian",
    "mlt": "Maltese",
    "msa": "Malay",
    "mya": "Burmese",
    "nep": "Nepali",
    "nld": "Dutch; Flemish",
    "nor": "Norwegian",
    "oci": "Occitan (post 1500)",
    "ori": "Oriya",
    "osd": "Orientation and script detection module",
    "pan": "Panjabi; Punjabi",
    "pol": "Polish",
    "por": "Portuguese",
    "pus": "Pushto; Pashto",
    "ron": "Romanian; Moldavian; Moldovan",
    "rus": "Russian",
    "san": "Sanskrit",
    "sin": "Sinhala; Sinhalese",
    "slk": "Slovak",
    "slv": "Slovenian",
    "spa": "Spanish",
    "sqi": "Albanian",
    "srp": "Serbian",
    "sun": "Sundanese",
    "swa": "Swahili",
    "swe": "Swedish",
    "syr": "Syriac",
    "tam": "Tamil",
    "tat": "Tatar",
    "tel": "Telugu",
    "tgk": "Tajik",
    "tgl": "Tagalog (new - Filipino)",
    "tha": "Thai",
    "tir": "Tigrinya",
    "ton": "Tonga",
    "tur": "Turkish",
    "uig": "Uighur; Uyghur",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "uzb": "Uzbek",
    "vie": "Vietnamese",
    "yid": "Yiddish",
    "yor": "Yoruba",
}
