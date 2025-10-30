from tkinter import *
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import os


MODEL_PATH = r"D:\SCHOOL\ZLERION\Projects\web_Summarise\web_summariser"

aismry = Tk()
aismry.title("AI Website Summariser")
aismry.state("zoom")
aismry.configure(bg="#efefef")
aismry.iconphoto(True, PhotoImage(file='icon.png'))


title_label = Label(aismry, text="🌐 AI Website Describer", font=("Dungeon", 30, "bold"), bg="#efefef", fg="#2e3f50").pack(pady=12)


try:
    summarizer = pipeline("summarization", model=MODEL_PATH, tokenizer=MODEL_PATH)
except Exception as e:
    messagebox.showerror("Model load error", f"Failed to load model:\n{e}")
    raise SystemExit


def get_website_text(url):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(paragraphs)
        return " ".join(text.split())
    except Exception as e:
        return f"__ERROR_FETCH__:{e}"


url_frame = Frame(aismry, bg="#efefef")
url_frame.pack(pady=8)

url_label = Label(url_frame, text="Enter Website URL:", font=("Dungeon", 12), bg="#efefef", fg="#2e3f50")
url_label.pack(side=LEFT, padx=6)

url_entry = Entry(url_frame, width=50, font=("Arial", 11), bg="#efefef", fg="#2e3f50", relief=SOLID)
url_entry.pack(side=LEFT, padx=6, ipady=4)
url_entry.focus_set()


summarize_btn = Button(url_frame, text="Summarize", font=("Dungeon", 11, "bold"), bg="#2e3f50", fg="#efefef", relief=RIDGE)
summarize_btn.pack(side=LEFT, padx=6)


progress = ttk.Progressbar(aismry, mode='indeterminate', length=400)
def show_progress():
    progress.pack(pady=10)
    progress.start()

def hide_progress():
    progress.stop()
    progress.pack_forget()


output_box = ScrolledText(aismry, wrap=WORD, font=("Arial", 12), bg="#FFFFFF", fg="#000000", height=30, width=100, relief=SOLID)
output_box.pack(padx=12, pady=50)
output_box.config(state=DISABLED)


def summarize_website():
    url = url_entry.get().strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if not url:
        messagebox.showwarning("Input Missing", "Please enter a website URL.")
        return

    summarize_btn.config(state="disabled")
    output_box.config(state="normal")
    output_box.delete(1.0, END)
    output_box.insert(END, "Fetching and analyzing website... Please wait.\n")
    output_box.config(state="disabled")

    show_progress()
    def run_summary():
        try:
            article_text = get_website_text(url)

            if len(article_text.strip()) < 100:
                result = "📄Content:\n\n" + article_text
            elif len(article_text.strip()) < 10:
                result = "⚠️ This website doesn't contain enough readable text to summarize."
            else:
                summary = summarizer(
                    article_text,
                    max_length=250,
                    min_length=25,
                    do_sample=False
                )[0]['summary_text']

                sentences = summary.split(". ")
                result = "\n\n".join([f"• {s.strip()}" + ("" if s.strip().endswith(".") else ".") for s in sentences if s.strip()])

            output_box.config(state="normal")
            output_box.delete(1.0, END)
            output_box.insert(END, result)
            output_box.config(state="disabled")

        except Exception as e:
            output_box.config(state="normal")
            output_box.delete(1.0, END)
            output_box.insert(END, f"Error: {e}")
            output_box.config(state="disabled")
        finally:
            summarize_btn.config(state="normal")
            hide_progress()  # 👈 hide when finished

    threading.Thread(target=run_summary, daemon=True).start()


summarize_btn.config(command=summarize_website)
aismry.bind('<Return>', lambda event: summarize_btn.invoke())

aismry.mainloop()
