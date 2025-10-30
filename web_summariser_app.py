import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# === Load local fine-tuned summarizer ===
MODEL_PATH = r"D:\SCHOOL\ZLERION\Projects\web_Summarise\web_summariser"

try:
    summarizer = pipeline(
        "summarization",
        model=MODEL_PATH,
        tokenizer=MODEL_PATH
    )
except Exception as e:
    messagebox.showerror("Error", f"Failed to load model.\n{e}")
    raise SystemExit

# === Extract website text ===
def get_website_text(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(paragraphs)
        return " ".join(text.split())  # clean spaces
    except Exception as e:
        return f"Error fetching website: {e}"

# === Summarize / Describe Website ===
def summarize_website():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Missing", "Please enter a website URL.")
        return

    # Disable UI during processing
    summarize_btn.config(state="disabled")
    progress.start()
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Fetching and analyzing website... Please wait.\n")

    def run_summary():
        try:
            article_text = get_website_text(url)

            if len(article_text.strip()) < 30:
                result = "⚠️ This website doesn't contain enough readable text to summarize."
            else:
                summary = summarizer(
                    article_text,
                    max_length=250,
                    min_length=25,
                    do_sample=False
                )[0]['summary_text']

                # Display point-wise sentences
                sentences = summary.split(". ")
                result = "\n".join([f"• {s.strip()}." for s in sentences if s.strip()])

            output_box.delete(1.0, tk.END)
            output_box.insert(tk.END, result)

        except Exception as e:
            output_box.delete(1.0, tk.END)
            output_box.insert(tk.END, f"❌ Error: {e}")
        finally:
            summarize_btn.config(state="normal")
            progress.stop()

    threading.Thread(target=run_summary, daemon=True).start()

# === Copy to Clipboard ===
def copy_summary():
    summary_text = output_box.get(1.0, tk.END).strip()
    if summary_text:
        root.clipboard_clear()
        root.clipboard_append(summary_text)
        messagebox.showinfo("Copied", "Summary copied to clipboard!")
    else:
        messagebox.showwarning("Empty", "No summary to copy.")

# === UI Setup ===
root = tk.Tk()
root.title("🌐 AI Website Describer")
root.geometry("800x600")
root.configure(bg="#f4f4f8")

# === Title ===
title_label = tk.Label(
    root,
    text="🌐 AI Website Describer",
    font=("Segoe UI", 20, "bold"),
    bg="#f4f4f8",
    fg="#333"
)
title_label.pack(pady=10)

# === URL Frame ===
url_frame = tk.Frame(root, bg="#f4f4f8")
url_frame.pack(pady=10)

url_label = tk.Label(url_frame, text="Enter Website URL:", font=("Segoe UI", 12), bg="#f4f4f8")
url_label.pack(side=tk.LEFT, padx=5)

url_entry = ttk.Entry(url_frame, width=60, font=("Segoe UI", 11))
url_entry.pack(side=tk.LEFT, padx=5)

summarize_btn = ttk.Button(url_frame, text="Summarize", command=summarize_website)
summarize_btn.pack(side=tk.LEFT, padx=5)

# === Progress Bar ===
progress = ttk.Progressbar(root, mode='indeterminate', length=400)
progress.pack(pady=10)

# === Output Box ===
output_box = ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11), bg="white", height=20)
output_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

# === Copy Button ===
copy_btn = ttk.Button(root, text="Copy Summary", command=copy_summary)
copy_btn.pack(pady=10)

# === Run App ===
root.mainloop()
