"""
Required imports
"""
from tkinter import TclError
from sys import platform
from services import (
    ttkb,
    save_as,
    os,
    dark_mode,
    light_mode,
    open_image_dialog,
    open_from_clipboard,
    clear_text,
    copy_all,
    capture_screen,
)

current_directory = os.getcwd()
RELATIVE_ICO_DIRECTORY ="media/icon.ico"
absolute_directory= os.path.join(current_directory,RELATIVE_ICO_DIRECTORY)

def menu_gui():
    """
    Create the menu for the tkinter application.
    Returns:
        None
    """
    root = ttkb.Window(
        title="Stringfy", themename="pulse", minsize=(450, 250), size=(900, 500)
    )
    try:
        root.iconbitmap(absolute_directory)
    except TclError:
        pass

    root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
    menu_elements(root)


def menu_elements(root):
    """
    Create the menu elements for the tkinter application.
    Args:
        root (ttkb.Tk): The tkinter root window.
    Returns:
        None
    """

    my_menu = ttkb.Menu(root)
    root.config(menu=my_menu)

    file_menu = ttkb.Menu(my_menu, tearoff="off")
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(
        label="Open image", command=lambda: open_image_dialog(text_display, root)
    )
    file_menu.add_command(label="Save as..", command=lambda: save_as(text_display))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    view_menu = ttkb.Menu(my_menu, tearoff="off")
    my_menu.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Dark mode", command=lambda: dark_mode(root))
    view_menu.add_command(label="Light mode", command=lambda: light_mode(root))

    # Options display buttons#

    options_frame = ttkb.Frame()
    options_frame.pack()

    btn_open = ttkb.Button(
        options_frame,
        text="Open image",
        bootstyle="success",
        command=lambda: open_image_dialog(text_display, root),
    )
    btn_open.pack(
        padx=2, pady=6, ipadx=10, ipady=10, expand=True, fill=ttkb.BOTH, side=ttkb.LEFT
    )

    btn_paste = ttkb.Button(
        options_frame,
        bootstyle="success",
        text="Paste clipboard",
        command=lambda: open_from_clipboard(text_display, root),
    )
    btn_paste.pack(
        padx=2, pady=6, ipadx=10, ipady=10, expand=True, fill=ttkb.BOTH, side=ttkb.LEFT
    )

    btn_capture = ttkb.Button(
        options_frame,
        bootstyle="success",
        text="Capture",
        command=lambda: capture_screen(text_display, root),
    )
    if platform != "win32":
        btn_capture["state"] = ttkb.DISABLED
    btn_capture.pack(
        padx=2, pady=6, ipady=10, ipadx=20, expand=True, fill=ttkb.BOTH, side=ttkb.LEFT
    )

    # Text display buttons#

    frame = ttkb.Frame(root)
    frame.pack(padx=20, pady=5)

    button_frame = ttkb.Frame(frame)
    button_frame.pack()

    btn_clear = ttkb.Button(
        button_frame,
        text="Clear",
        bootstyle="info-outline",
        command=lambda: clear_text(text_display),
    )
    btn_clear.pack(
        padx=2, pady=4, ipadx=20, expand=True, fill=ttkb.BOTH, side=ttkb.LEFT
    )

    btn_copy = ttkb.Button(
        button_frame,
        text="Copy all",
        bootstyle="info-outline",
        command=lambda: copy_all(text_display, root),
    )
    btn_copy.pack(padx=2, pady=4, ipadx=10, expand=True, fill=ttkb.BOTH, side=ttkb.LEFT)

    # Text display frame#

    scroll_bar = ttkb.Scrollbar(frame, orient="vertical")
    scroll_bar.pack(side="right", fill="y")

    text_display = ttkb.Text(
        frame, height=500, width=300, yscrollcommand=scroll_bar.set
    )
    text_display.insert(ttkb.END, "")
    text_display.pack(side="left")

    root.mainloop()
