"""PaperView: a small Windows-friendly PDF reader built with Tkinter and PyMuPDF."""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import fitz
from PIL import Image, ImageTk


BG = "#edf1f6"
INK = "#202a36"
ACCENT = "#1769d2"


class PaperView:
    def __init__(self, root):
        self.root = root
        self.root.title("PaperView — PDF reader")
        self.root.geometry("1120x780")
        self.root.minsize(720, 500)
        self.root.configure(bg=BG)
        self.doc = None
        self.path = None
        self.page_num = 0
        self.zoom = 1.0
        self.fit_mode = "page"
        self.photo = None
        self.search_hits = []
        self.hit_index = -1
        self.resize_job = None
        self._build_ui()
        self._bind_keys()
        self._show_welcome()

    def _build_ui(self):
        bar = tk.Frame(self.root, bg="#ffffff", height=58, padx=12)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self._button(bar, "Open PDF", self.open_pdf, primary=True).pack(side="left", pady=9)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12, pady=12)
        self._button(bar, "‹", lambda: self.change_page(-1), width=3).pack(side="left")
        self.page_var = tk.StringVar(value="—")
        self.page_entry = tk.Entry(bar, textvariable=self.page_var, width=5, justify="center", relief="solid", bd=1)
        self.page_entry.pack(side="left", padx=(5, 4), ipady=5)
        self.page_entry.bind("<Return>", self.go_to_page)
        self.page_total = tk.Label(bar, text="of —", bg="white", fg="#657184", font=("Segoe UI", 9))
        self.page_total.pack(side="left", padx=(0, 5))
        self._button(bar, "›", lambda: self.change_page(1), width=3).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12, pady=12)
        self._button(bar, "−", lambda: self.set_zoom(self.zoom / 1.2), width=3).pack(side="left")
        self.zoom_label = tk.Label(bar, text="100%", width=6, bg="white", fg=INK, font=("Segoe UI", 9))
        self.zoom_label.pack(side="left")
        self._button(bar, "+", lambda: self.set_zoom(self.zoom * 1.2), width=3).pack(side="left")
        self._button(bar, "Fit page", lambda: self.set_fit("page")).pack(side="left", padx=(8, 3))
        self._button(bar, "Fit width", lambda: self.set_fit("width")).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12, pady=12)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(bar, textvariable=self.search_var, width=22, relief="solid", bd=1,
                                     font=("Segoe UI", 9))
        self.search_entry.pack(side="left", ipady=6)
        self.search_entry.insert(0, "Find in document")
        self.search_entry.bind("<FocusIn>", self._clear_search_hint)
        self.search_entry.bind("<Return>", lambda _e: self.search())
        self._button(bar, "Find", self.search, primary=True).pack(side="left", padx=(5, 0))
        self._button(bar, "Print", self.print_pdf).pack(side="right", pady=9)

        self.filename = tk.Label(self.root, text="", anchor="w", bg=BG, fg="#627084",
                                 font=("Segoe UI", 9), padx=18, pady=7)
        self.filename.pack(fill="x")
        area = tk.Frame(self.root, bg=BG)
        area.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(area, bg="#e4e9f0", highlightthickness=0)
        self.vscroll = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        self.hscroll = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")
        self.hscroll.pack(fill="x")
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind_all("<MouseWheel>", self._mousewheel)
        self.canvas.bind_all("<Control-MouseWheel>", self._ctrl_wheel)

        self.status = tk.Label(self.root, text="Ready", anchor="w", bg="#ffffff", fg="#657184",
                               font=("Segoe UI", 9), padx=14, pady=6)
        self.status.pack(fill="x")

    def _button(self, parent, text, command, primary=False, width=None):
        opts = {"bg": ACCENT if primary else "#f2f5f9", "fg": "white" if primary else INK,
                "activebackground": "#0e57b7" if primary else "#e6ebf2", "activeforeground": "white" if primary else INK,
                "relief": "flat", "bd": 0, "font": ("Segoe UI", 9, "bold" if primary else "normal"),
                "cursor": "hand2", "padx": 11, "pady": 7, "command": command}
        if width:
            opts["width"] = width
            opts["padx"] = 2
        return tk.Button(parent, text=text, **opts)

    def _bind_keys(self):
        self.root.bind("<Control-o>", lambda _e: self.open_pdf())
        self.root.bind("<Control-f>", lambda _e: self.search_entry.focus_set())
        self.root.bind("<Control-p>", lambda _e: self.print_pdf())
        self.root.bind("<Prior>", lambda _e: self.change_page(-1))
        self.root.bind("<Next>", lambda _e: self.change_page(1))
        self.root.bind("<Left>", lambda _e: self.change_page(-1))
        self.root.bind("<Right>", lambda _e: self.change_page(1))

    def _show_welcome(self):
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 1000, 700))
        self.canvas.create_text(500, 255, text="Your PDFs, ready to read", fill=INK,
                                font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(500, 300, text="Open a PDF to get started. Use the toolbar to move through pages, zoom, search, and print.",
                                fill="#657184", font=("Segoe UI", 11), width=600, justify="center")
        self.canvas.create_text(500, 360, text="Ctrl + O   Open PDF      Ctrl + F   Find      Ctrl + P   Print", fill="#657184",
                                font=("Segoe UI", 10))

    def open_pdf(self, path=None):
        if not path:
            path = filedialog.askopenfilename(title="Open PDF", filetypes=[("PDF documents", "*.pdf"), ("All files", "*.*")])
        if not path:
            return
        try:
            new_doc = fitz.open(path)
            if not new_doc.page_count:
                raise ValueError("This PDF has no pages.")
            if self.doc:
                self.doc.close()
            self.doc = new_doc
            self.path = path
            self.page_num = 0
            self.fit_mode = "page"
            self.search_hits = []
            self.hit_index = -1
            self.root.title(f"{os.path.basename(path)} — PaperView")
            self.filename.configure(text=os.path.basename(path))
            self.status.configure(text=f"{self.doc.page_count} pages")
            self.render_page()
        except Exception as exc:
            messagebox.showerror("Could not open PDF", f"PaperView couldn't open this file.\n\n{exc}")

    def render_page(self):
        if not self.doc:
            return
        page = self.doc.load_page(self.page_num)
        width = max(200, self.canvas.winfo_width() - 56)
        height = max(200, self.canvas.winfo_height() - 32)
        if self.fit_mode == "page":
            self.zoom = min(width / page.rect.width, height / page.rect.height)
        elif self.fit_mode == "width":
            self.zoom = width / page.rect.width
        self.zoom = max(0.2, min(self.zoom, 4.0))
        matrix = fitz.Matrix(self.zoom * 1.45, self.zoom * 1.45)
        pix = page.get_pixmap(matrix=matrix, alpha=False, annots=True)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        cw = max(width + 56, pix.width + 56)
        ch = max(height + 32, pix.height + 32)
        self.canvas.configure(scrollregion=(0, 0, cw, ch))
        x = max(28, (cw - pix.width) // 2)
        self.canvas.create_image(x, 16, image=self.photo, anchor="nw")
        self.canvas.create_rectangle(x - 1, 15, x + pix.width + 1, 17 + pix.height, outline="#c6ced9")
        self.page_var.set(str(self.page_num + 1))
        self.page_total.configure(text=f"of {self.doc.page_count}")
        self.zoom_label.configure(text=f"{round(self.zoom * 100)}%")
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.status.configure(text=f"Page {self.page_num + 1} of {self.doc.page_count}  ·  {round(self.zoom * 100)}%")

    def change_page(self, offset):
        if self.doc:
            new_page = max(0, min(self.doc.page_count - 1, self.page_num + offset))
            if new_page != self.page_num:
                self.page_num = new_page
                self.render_page()

    def go_to_page(self, _event=None):
        if not self.doc:
            return
        try:
            target = int(self.page_var.get()) - 1
            if target < 0 or target >= self.doc.page_count:
                raise ValueError
            self.page_num = target
            self.render_page()
        except ValueError:
            self.page_var.set(str(self.page_num + 1))

    def set_zoom(self, zoom):
        if not self.doc:
            return
        self.fit_mode = "manual"
        self.zoom = max(0.2, min(zoom, 4.0))
        self.render_page()

    def set_fit(self, mode):
        if self.doc:
            self.fit_mode = mode
            self.render_page()

    def _on_resize(self, _event):
        if self.doc and self.fit_mode in ("page", "width"):
            if self.resize_job:
                self.root.after_cancel(self.resize_job)
            self.resize_job = self.root.after(180, self.render_page)

    def _mousewheel(self, event):
        if event.state & 0x0004:
            return
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _ctrl_wheel(self, event):
        self.set_zoom(self.zoom * (1.1 if event.delta > 0 else 1 / 1.1))

    def _clear_search_hint(self, _event):
        if self.search_entry.get() == "Find in document":
            self.search_entry.delete(0, "end")

    def search(self):
        if not self.doc:
            return
        query = self.search_var.get().strip()
        if not query or query == "Find in document":
            return
        if not self.search_hits or query != getattr(self, "last_query", None):
            self.search_hits = []
            self.last_query = query
            for pno in range(self.doc.page_count):
                for rect in self.doc.load_page(pno).search_for(query):
                    self.search_hits.append((pno, rect))
            self.hit_index = -1
        if not self.search_hits:
            self.status.configure(text=f'No matches for “{query}”')
            return
        self.hit_index = (self.hit_index + 1) % len(self.search_hits)
        pno, rect = self.search_hits[self.hit_index]
        self.page_num = pno
        self.render_page()
        scale = self.zoom * 1.45
        self.canvas.yview_moveto(max(0, (rect.y0 * scale - 50) / max(1, self.canvas.bbox("all")[3])))
        self.status.configure(text=f'Match {self.hit_index + 1} of {len(self.search_hits)} for “{query}”  ·  Page {pno + 1}')

    def print_pdf(self):
        if not self.path:
            messagebox.showinfo("Print", "Open a PDF first.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(self.path, "print")
            else:
                import subprocess
                subprocess.Popen(["open", "-a", "Preview", self.path])
                messagebox.showinfo("Print", "The PDF is open in your system PDF app. Use its Print command.")
        except Exception as exc:
            messagebox.showerror("Print", f"Couldn't send this PDF to the printer.\n\n{exc}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PaperView(root)
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app.open_pdf(sys.argv[1])
    root.mainloop()
