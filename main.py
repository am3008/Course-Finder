import tkinter as tk
from tkinter import messagebox, Entry, Button, PhotoImage
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# Constants
SAVE_FILE = "save.txt"
URL_TEMPLATE = "https://sis.rutgers.edu/soc/#keyword?keyword={}&semester=12020&campus=NB&level=U"
SEARCH_BTN_HEIGHT = 5
SEARCH_BTN_WIDTH = 13
BG_COLOR = "#FF5733"
FONT_STYLE = "Arial 20 bold"

def update_text(canvas, now_open, closed):
    canvas.delete("text")
    canvas.create_text(285, 450, fill="white", font="Arial 20 bold", text="\n\n" + now_open + closed, tag="text")

def check_course_availability(index, driver):
    index_nospace = index.strip()
    if not index_nospace:
        return None, None, None

    url = URL_TEMPLATE.format(index_nospace)
    print(url)
    driver.get(url)
    driver.refresh()
    time.sleep(2)
    html = driver.page_source
    is_open = "section sectionStatus_open" in html

    index_of_class = html.find("courseMetadata.title")
    end_index = html.find('<', index_of_class)
    class_name = html[index_of_class + 22:end_index]

    return index_nospace, class_name, is_open

def course_search(email_id, phone_number, index_list, driver_path, canvas):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(driver_path, options=chrome_options)
    now_open = ""
    closed = ""

    while index_list:
        print(index_list)
        deletions = []
        for index in index_list:
            index_nospace, class_name, is_open = check_course_availability(index, driver)
            if index_nospace is None:
                continue

            status = "Open" if is_open else "Closed"
            print(f"{index_nospace}: {class_name} - {status}")
            if is_open:
                deletions.append(index)
                now_open += f"{index_nospace}\t{class_name}:\tOpen\n\n"
                notify(email_id, phone_number, class_name, URL_TEMPLATE.format(index_nospace))
            else:
                closed += f"{index_nospace}\t{class_name}:\tClosed\n\n"

            update_text(canvas, now_open, closed)
            canvas.update()

        for num in deletions:
            index_list.remove(num)

    driver.close()
    driver.quit()

def grab_data(entry_fields, canvas):
    email_id, phone_number, driver_path, index_list = (entry.get() for entry in entry_fields)
    index_list_separated = index_list.split(",")
    
    if not all([email_id, phone_number, index_list, driver_path]):
        messagebox.showinfo("Message", "Please Enter All Data")
    else:
        update_text(canvas, "", "")
        with open(SAVE_FILE, "w") as f:
            f.write(','.join([email_id, phone_number, driver_path, index_list]))
        course_search(email_id, phone_number, index_list_separated, driver_path, canvas)

def setup_gui():
    root = tk.Tk()
    root.resizable(False, False)
    root.title("Rutgers Course Searcher")
    root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file='ico.png'))

    hheight = root.winfo_screenheight()
    wwidth = root.winfo_screenwidth()
    canvas = tk.Canvas(root, height=hheight/1.5, width=wwidth/1.5, bg=BG_COLOR)
    canvas.pack()
    update_text(canvas, "", "")
    canvas.create_text(wwidth/4+125, 60, text="Rutgers Course Searcher", anchor="center", fill="white", font="Arial 40 bold")

    y_increase = 130
    entry_fields = create_input_fields(canvas, y_increase)

    enter_data_btn = Button(canvas, text="Search Courses", command=lambda: grab_data(entry_fields, canvas))
    enter_data_btn.config(height=SEARCH_BTN_HEIGHT, width=SEARCH_BTN_WIDTH)
    canvas.create_window(800, 225, window=enter_data_btn)

    canvas.pack()
    root.mainloop()

def create_input_fields(canvas, y_increase):
    input_labels = ["Enter Email:", "Enter Phone Number:", "Enter Driver Path:", "Enter Indexes (separated by comma):"]
    entry_fields = []

    for i, label in enumerate(input_labels):
        canvas.create_text(190, (i * 50) + y_increase, fill="white", font=FONT_STYLE, text=label)
        entry = Entry(canvas)
        entry_fields.append(entry)
        canvas.create_window(500, (i * 50) + y_increase, window=entry)

    # Load saved data if available
    if os.path.isfile(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            saved_data = f.read().split(",")
            for entry, data in zip(entry_fields, saved_data):
                entry.insert(tk.END, data)

    return entry_fields

if __name__ == "__main__":
    setup_gui()
