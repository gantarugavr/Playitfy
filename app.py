import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import threading
import time
import random
import sys
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.wave import WAVE
from PIL import Image, ImageTk, ImageDraw
import io

# ─── BACA MASTER VOLUME WINDOWS (Persistent Tracker) ────────────────────────
SYSTEM_VOLUME = "N/A"

def _volume_tracker():
    global SYSTEM_VOLUME
    try:
        import comtypes
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        comtypes.CoInitialize() 
    except Exception:
        return

    while True:
        try:
            devices = AudioUtilities.GetSpeakers()
            if devices is not None:
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                val = int(volume.GetMasterVolumeLevelScalar() * 100)
                SYSTEM_VOLUME = f"{val}%"
            else:
                SYSTEM_VOLUME = "N/A"
        except Exception:
            SYSTEM_VOLUME = "N/A"
        time.sleep(1) 

threading.Thread(target=_volume_tracker, daemon=True).start()

# ─── PYGAME INIT ─────────────────────────────────────────────────────────────
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# ─── PALETTE ─────────────────────────────────────────────────────────────────
BG_CREAM   = "#FCF3DE"
BG_LIGHT   = "#F5E6C8"
BG_SIDEBAR = "#EFD9A8"
RED_DARK   = "#A31616"
RED_MED    = "#C41E1E"
DARK_TXT   = "#2C0F0F"
MED_TXT    = "#3A1010"
LIGHT_TXT  = "#7A4040"
WHITE      = "#FFFFFF"
BORDER     = "#2C0F0F"
HOVER      = "#E8CC90"
SEL_BG     = "#A31616"
SEL_FG     = "#FFFFFF"

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_time(s):
    s = max(0, int(s))
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"

def make_thumb(pil_img, size=44):
    img = pil_img.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,size,size], radius=7, fill=255)
    out = Image.new("RGBA", (size, size), (0,0,0,0))
    out.paste(img, mask=mask)
    return out

def default_art(size=44, bg="#C8A060", fg="#A31616"):
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)
    mid = size // 2
    bars = [0.3, 0.55, 0.8, 1.0, 0.7, 0.9, 0.5, 0.35]
    bw = max(2, size // (len(bars) * 2))
    for i, h in enumerate(bars):
        bh = int(size * 0.65 * h)
        x = i * bw * 2 + 3
        d.rectangle([x, mid - bh // 2, x + bw, mid + bh // 2], fill=fg)
    return img

# ─── TUTORIAL WINDOW ─────────────────────────────────────────────────────────
class TutorialWindow(tk.Toplevel):
    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.title("Playitfy - Guide")
        self.geometry("640x500")
        self.resizable(False, False)
        self.configure(bg=BG_CREAM)
        self.grab_set()
        self._on_done = on_done

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"640x500+{(sw-640)//2}+{(sh-500)//2}")

        hdr = tk.Frame(self, bg=RED_DARK, height=64)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="▶ PLAYITFY", font=("Arial", 16, "bold"), fg=WHITE, bg=RED_DARK).pack(side=tk.LEFT, padx=22, pady=14)

        steps = [
            ("📂", "Select Folder", "Click 'Select Folder' on the left sidebar to load your MP3/WAV library."),
            ("🖱️", "Single Click = Play", "Click once on any track in the list to start playback. No double-click needed."),
            ("⏩", "Seekbar", "Click or drag the progress line to jump to a specific time precisely."),
            ("🔊", "App Volume", "The volume slider adjusts internal application sound, independent of the System Master Volume."),
            ("🔀", "Shuffle & Repeat", "Randomize track order, repeat all tracks, or loop a single track infinitely."),
            ("🪟", "Mini Player", "Click [Mini] for compact mode. LEFT CLICK and drag on the title to move the window anywhere."),
        ]

        outer = tk.Frame(self, bg=BG_CREAM)
        outer.pack(fill=tk.BOTH, expand=True)
        cv = tk.Canvas(outer, bg=BG_CREAM, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(cv, bg=BG_CREAM)
        cv.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))

        for icon, title, desc in steps:
            row = tk.Frame(inner, bg=BG_CREAM, pady=2)
            row.pack(fill=tk.X, padx=20, pady=4)
            icon_box = tk.Frame(row, bg=RED_DARK, width=42, height=42)
            icon_box.pack(side=tk.LEFT, padx=(0,14))
            icon_box.pack_propagate(False)
            tk.Label(icon_box, text=icon, font=("Segoe UI Emoji", 16), fg=WHITE, bg=RED_DARK).place(relx=0.5, rely=0.5, anchor="center")
            txt = tk.Frame(row, bg=BG_CREAM)
            txt.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(txt, text=title, font=("Arial", 10, "bold"), fg=DARK_TXT, bg=BG_CREAM, anchor="w").pack(fill=tk.X)
            tk.Label(txt, text=desc, font=("Arial", 9), fg=MED_TXT, bg=BG_CREAM, anchor="w", justify="left", wraplength=450).pack(fill=tk.X)

        foot = tk.Frame(self, bg=BG_LIGHT, pady=10)
        foot.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(foot, text="  Start Listening ▶  ", font=("Arial", 11, "bold"), bg=RED_DARK, fg=WHITE, relief=tk.SOLID, bd=2, cursor="hand2", command=self._done).pack()

    def _done(self):
        self.destroy()
        if self._on_done:
            self._on_done()

# ─── MINI PLAYER ─────────────────────────────────────────────────────────────
class MiniPlayer(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.configure(bg=BORDER)
        W, H = 342, 82
        sh = self.winfo_screenheight()
        self.geometry(f"{W}x{H}+12+{sh - H - 48}")

        self._dx = self._dy = 0
        outer = tk.Frame(self, bg=RED_DARK)
        outer.place(x=1, y=1, width=340, height=80)

        self.art_lbl = tk.Label(outer, bg="#5A0808", width=72, height=72)
        self.art_lbl.place(x=0, y=0, width=72, height=80)

        info = tk.Frame(outer, bg=RED_DARK)
        info.place(x=76, y=6, width=180, height=68)
        self.lbl_title = tk.Label(info, text="No Track", font=("Arial", 9, "bold"), fg=WHITE, bg=RED_DARK, anchor="w")
        self.lbl_title.pack(fill=tk.X)
        self.lbl_artist = tk.Label(info, text="—", font=("Arial", 8), fg="#FFCCCC", bg=RED_DARK, anchor="w")
        self.lbl_artist.pack(fill=tk.X)
        self.lbl_time = tk.Label(info, text="0:00 / 0:00", font=("Courier New", 8), fg="#FF9999", bg=RED_DARK, anchor="w")
        self.lbl_time.pack(fill=tk.X, pady=(2,0))

        self.mini_cv = tk.Canvas(info, height=4, bg="#5A0808", highlightthickness=0)
        self.mini_cv.pack(fill=tk.X, pady=(4,0))

        btns = tk.Frame(outer, bg=RED_DARK)
        btns.place(x=260, y=0, width=80, height=80)
        bst = dict(bg=RED_DARK, fg=WHITE, relief=tk.FLAT, bd=0, activebackground="#5A0808", cursor="hand2", font=("Arial", 11))

        tk.Button(btns, text="⏮", command=app.prev_track, **bst).grid(row=0, column=0, padx=2, pady=4)
        self.btn_play = tk.Button(btns, text="▶", command=app.toggle_play, **bst)
        self.btn_play.grid(row=0, column=1, padx=2, pady=4)
        tk.Button(btns, text="⏭", command=app.next_track, **bst).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btns, text="✕", command=app.close_mini, bg=RED_DARK, fg="#FF8080", relief=tk.FLAT, bd=0, activebackground="#5A0808", cursor="hand2", font=("Arial", 9)).grid(row=1, column=1, padx=2, pady=2)

        for w in [outer, info, self.lbl_title, self.lbl_artist, self.art_lbl]:
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_go)
        self._show_default_art()

    def _show_default_art(self):
        img = default_art(size=72, bg="#5A0808", fg=RED_DARK)
        self._def_photo = ImageTk.PhotoImage(img.convert("RGB"))
        self.art_lbl.config(image=self._def_photo)

    def _drag_start(self, e):
        self._dx, self._dy = e.x_root - self.winfo_x(), e.y_root - self.winfo_y()

    def _drag_go(self, e):
        self.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")

    def update_all(self, title, artist, art_photo, play_icon, cur_t, tot_t, pct):
        self.lbl_title.config(text=title[:20])
        self.lbl_artist.config(text=artist[:20])
        self.lbl_time.config(text=f"{cur_t} / {tot_t}")
        self.btn_play.config(text=play_icon)
        if art_photo:
            self.art_lbl.config(image=art_photo)
        w = self.mini_cv.winfo_width()
        if w > 2:
            self.mini_cv.delete("all")
            self.mini_cv.create_rectangle(0,0,w,4, fill="#5A0808", outline="")
            fw = int(w * pct)
            if fw > 0:
                self.mini_cv.create_rectangle(0,0,fw,4, fill="#FFCCCC", outline="")

# ─── MAIN APP ────────────────────────────────────────────────────────────────
class MusicPlayerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Playitfy - Music Player")
        self.master.configure(bg=BG_CREAM)
        sw, sh = master.winfo_screenwidth(), master.winfo_screenheight()
        W, H = min(1100, sw), min(660, sh)
        self.master.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.master.minsize(860, 540)

        self.playlist      = []
        self.current_idx   = -1
        self.is_paused     = False
        self.is_playing    = False
        self.track_len     = 0.0
        self.is_shuffle    = False
        self.repeat_mode   = 0
        self._was_busy     = False
        self._lock         = threading.Lock()
        self._loading      = False          

        self._seek_pct      = 0.0
        self._dragging_seek = False
        self._play_offset   = 0.0

        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)

        self.mini             = None
        self._mini_art_photo  = None
        self._large_art_photo = None
        self._thumb_cache     = {}
        self._tick_count      = 0

        pygame.mixer.music.set_volume(0.5)

        self.footer_text = "© 2026 Project ❄️ gantarugavr.me"

        self._build_ui()
        self._search_var.trace_add("write", lambda *a: self._filter_list())
        self._tick()
        self.master.after(300, self._show_tutorial)

    def _build_ui(self):
        self._build_topbar()
        body = tk.Frame(self.master, bg=BG_CREAM)
        body.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar(body)
        self._build_player(body)

        footer_frame = tk.Frame(self.master, bg=BG_CREAM)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_footer = tk.Label(footer_frame, text=self.footer_text,
                                   font=("Arial", 9, "bold"), fg=DARK_TXT, bg=BG_CREAM)
        self.lbl_footer.pack(side=tk.RIGHT, padx=15, pady=5)

    def _integrity_guard(self):
        if self._loading:
            return
        try:
            # Jika ada yang menghapus copyright footer, matikan aplikasi
            if self.lbl_footer.cget("text") != self.footer_text:
                sys.exit()
        except Exception:
            pass

    def _build_topbar(self):
        bar = tk.Frame(self.master, bg=RED_DARK, height=48)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="▶ PLAYITFY", font=("Arial", 14, "bold"),
                 fg=WHITE, bg=RED_DARK).pack(side=tk.LEFT, padx=18, pady=10)

        ctrls = tk.Frame(bar, bg=RED_DARK)
        ctrls.pack(side=tk.RIGHT, padx=10)
        tk.Button(ctrls, text="❓ Help", font=("Arial", 9, "bold"), bg="#6A0808", fg=WHITE,
                  activebackground=RED_MED, relief=tk.SOLID, bd=1, padx=10, pady=5,
                  cursor="hand2", command=self._show_tutorial).pack(side=tk.LEFT, padx=3)
        tk.Button(ctrls, text="Mini", font=("Arial", 9, "bold"), bg="#6A0808", fg=WHITE,
                  activebackground=RED_MED, relief=tk.SOLID, bd=1, padx=10, pady=5,
                  cursor="hand2", command=self._toggle_mini).pack(side=tk.LEFT, padx=3)

        self.lbl_ticker = tk.Label(bar, text="  Enjoy the music ✦  ",
                                   font=("Arial", 9, "bold"), fg="#FFCCCC", bg=RED_DARK)
        self.lbl_ticker.pack(side=tk.LEFT, padx=16)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG_SIDEBAR, width=268)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        tk.Button(sb, text="📂  Select Folder", font=("Arial", 10, "bold"),
                  bg=RED_DARK, fg=WHITE, activebackground=RED_MED, relief=tk.SOLID,
                  bd=2, padx=14, pady=10, cursor="hand2",
                  command=self.load_folder).pack(fill=tk.X, padx=14, pady=(14,4))

        self.lbl_path = tk.Label(sb, text="Folder: -",
                                 font=("Courier New", 8, "italic"), fg=LIGHT_TXT,
                                 bg=BG_SIDEBAR, anchor="w")
        self.lbl_path.pack(fill=tk.X, padx=16, pady=(0,6))

        sf = tk.Frame(sb, bg=BORDER, bd=1)
        sf.pack(fill=tk.X, padx=14, pady=(0,6))
        self._search_var = tk.StringVar()
        self.search_entry = tk.Entry(sf, textvariable=self._search_var,
                                     font=("Arial", 9, "bold"), bg=BG_LIGHT,
                                     fg=DARK_TXT, relief=tk.FLAT, bd=6)
        self.search_entry.pack(fill=tk.X)

        self.lbl_count = tk.Label(sb, text="0 tracks", font=("Arial", 8, "bold"),
                                  fg=LIGHT_TXT, bg=BG_SIDEBAR)
        self.lbl_count.pack(anchor="w", padx=16, pady=(0,4))

        lf = tk.Frame(sb, bg=BG_SIDEBAR)
        lf.pack(fill=tk.BOTH, expand=True)
        self._tcanvas = tk.Canvas(lf, bg=BG_LIGHT, highlightthickness=0, bd=0)
        vs = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._tcanvas.yview)
        self._tcanvas.configure(yscrollcommand=vs.set)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        self._tcanvas.pack(fill=tk.BOTH, expand=True)

        self._tinner = tk.Frame(self._tcanvas, bg=BG_LIGHT)
        self._twin   = self._tcanvas.create_window((0,0), window=self._tinner, anchor="nw")
        self._tinner.bind("<Configure>",
                          lambda e: self._tcanvas.configure(scrollregion=self._tcanvas.bbox("all")))
        self._tcanvas.bind("<Configure>",
                           lambda e: self._tcanvas.itemconfig(self._twin, width=e.width))

    def _build_player(self, parent):
        pf = tk.Frame(parent, bg=BG_CREAM)
        pf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        nrow = tk.Frame(pf, bg=BG_CREAM)
        nrow.pack(fill=tk.X, padx=28, pady=(22,0))

        art_outer = tk.Frame(nrow, bg=BORDER, bd=2)
        art_outer.pack(side=tk.LEFT)
        self.art_lbl = tk.Label(art_outer, bg=BG_SIDEBAR, width=134, height=134)
        self.art_lbl.pack(padx=2, pady=2)
        self._show_default_large_art()

        meta = tk.Frame(nrow, bg=BG_CREAM)
        meta.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        tk.Label(meta, text="NOW PLAYING", font=("Courier New", 9, "bold"),
                 fg=RED_DARK, bg=BG_CREAM).pack(anchor="w")
        self.lbl_title = tk.Label(meta, text="—", font=("Arial", 18, "bold"),
                                  fg=DARK_TXT, bg=BG_CREAM, anchor="w", justify="left")
        self.lbl_title.pack(fill=tk.X, pady=(4,2))
        self.lbl_artist = tk.Label(meta, text="Artist: Choose music folder",
                                   font=("Arial", 10, "bold"), fg=MED_TXT,
                                   bg=BG_CREAM, anchor="w")
        self.lbl_artist.pack(fill=tk.X)
        self.lbl_type = tk.Label(meta, text="Format: —", font=("Arial", 10, "bold"),
                                 fg=LIGHT_TXT, bg=BG_CREAM, anchor="w")
        self.lbl_type.pack(fill=tk.X, pady=(2,0))

        srow = tk.Frame(pf, bg=BG_CREAM)
        srow.pack(fill=tk.X, padx=28, pady=(16,0))

        trow = tk.Frame(srow, bg=BG_CREAM)
        trow.pack(fill=tk.X)
        self.lbl_cur   = tk.Label(trow, text="0:00", font=("Courier New", 9, "bold"),
                                  fg=DARK_TXT, bg=BG_CREAM)
        self.lbl_cur.pack(side=tk.LEFT)
        self.lbl_total = tk.Label(trow, text="0:00", font=("Courier New", 9, "bold"),
                                  fg=DARK_TXT, bg=BG_CREAM)
        self.lbl_total.pack(side=tk.RIGHT)

        self.seekbar = tk.Canvas(srow, height=24, bg=BG_CREAM,
                                 highlightthickness=0, cursor="hand2")
        self.seekbar.pack(fill=tk.X, pady=(4,0))
        self.seekbar.bind("<ButtonPress-1>",   self._seek_press)
        self.seekbar.bind("<B1-Motion>",       self._seek_drag)
        self.seekbar.bind("<ButtonRelease-1>", self._seek_release)
        self.seekbar.bind("<Configure>",       lambda e: self._draw_seek())

        vrow_container = tk.Frame(srow, bg=BG_CREAM)
        vrow_container.pack(fill=tk.X, pady=(15,0))
        vrow = tk.Frame(vrow_container, bg=BG_CREAM)
        vrow.pack(anchor=tk.CENTER)

        tk.Label(vrow, text="🔊 Vol App:", font=("Arial", 9, "bold"),
                 fg=DARK_TXT, bg=BG_CREAM).pack(side=tk.LEFT)
        self._vol_sl = tk.Scale(vrow, from_=0, to=100, orient=tk.HORIZONTAL,
                                bg=BG_CREAM, troughcolor=BG_LIGHT, highlightthickness=0,
                                relief=tk.SOLID, bd=1, activebackground=RED_DARK,
                                length=150, showvalue=False, command=self._on_vol)
        self._vol_sl.set(50)
        self._vol_sl.pack(side=tk.LEFT, padx=6)
        self.lbl_vol = tk.Label(vrow, text="50%", font=("Courier New", 9, "bold"),
                                fg=DARK_TXT, bg=BG_CREAM, width=4)
        self.lbl_vol.pack(side=tk.LEFT)

        tk.Frame(vrow, bg=BORDER, width=1, height=18).pack(side=tk.LEFT, padx=12)
        tk.Label(vrow, text="🖥 System:", font=("Arial", 9, "bold"),
                 fg=DARK_TXT, bg=BG_CREAM).pack(side=tk.LEFT)
        
        self.lbl_master = tk.Label(vrow, text=SYSTEM_VOLUME, font=("Courier New", 9, "bold"),
                                   fg=MED_TXT, bg=BG_CREAM)
        self.lbl_master.pack(side=tk.LEFT, padx=(4,0))

        self._build_controls(pf)

    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=BG_CREAM)
        ctrl.pack(pady=(20,0))

        ss = dict(bg=BG_LIGHT, fg=DARK_TXT, activebackground=HOVER, relief=tk.SOLID,
                  bd=2, font=("Arial", 13, "bold"), cursor="hand2", width=5, pady=6)
        ps = dict(bg=RED_DARK, fg=WHITE, activebackground=RED_MED, relief=tk.SOLID,
                  bd=2, font=("Arial", 15, "bold"), cursor="hand2", width=9, pady=4)

        self.btn_shuffle = tk.Button(ctrl, text="🔀", command=self.toggle_shuffle, **ss)
        self.btn_shuffle.grid(row=0, column=0, padx=5)
        tk.Button(ctrl, text="⏮", command=self.prev_track,              **ss).grid(row=0, column=1, padx=5)
        tk.Button(ctrl, text="⏪", command=lambda: self.skip_time(-10), **ss).grid(row=0, column=2, padx=5)
        self.btn_play = tk.Button(ctrl, text="▶ PLAY", command=self.toggle_play, **ps)
        self.btn_play.grid(row=0, column=3, padx=12)
        tk.Button(ctrl, text="⏩", command=lambda: self.skip_time(10),  **ss).grid(row=0, column=4, padx=5)
        tk.Button(ctrl, text="⏭", command=self.next_track,              **ss).grid(row=0, column=5, padx=5)
        self.btn_repeat = tk.Button(ctrl, text="🔁 Off", command=self.toggle_repeat,
                                    bg=BG_LIGHT, fg=DARK_TXT, activebackground=HOVER,
                                    relief=tk.SOLID, bd=2, font=("Arial", 11, "bold"),
                                    cursor="hand2", width=7, pady=6)
        self.btn_repeat.grid(row=0, column=6, padx=5)

    def _show_default_large_art(self):
        img = default_art(size=130, bg=BG_SIDEBAR, fg=RED_DARK)
        self._def_large = ImageTk.PhotoImage(img.convert("RGB"))
        self.art_lbl.config(image=self._def_large)

    def _set_large_art(self, pil_img):
        img = pil_img.resize((130,130), Image.Resampling.LANCZOS).convert("RGB")
        self._large_art_photo = ImageTk.PhotoImage(img)
        self.art_lbl.config(image=self._large_art_photo)

    def _render_rows(self, indices=None):
        for w in self._tinner.winfo_children():
            w.destroy()
        self._track_rows = []
        pool = [(i, self.playlist[i]) for i in range(len(self.playlist))]
        if indices is not None:
            pool = [(i, self.playlist[i]) for i in indices]
        for rn, (idx, trk) in enumerate(pool):
            self._add_row(rn, idx, trk)

    def _add_row(self, rn, idx, trk):
        is_cur = (idx == self.current_idx)
        bg  = SEL_BG if is_cur else (BG_CREAM if rn%2==0 else BG_LIGHT)
        fg  = SEL_FG if is_cur else DARK_TXT
        fg2 = "#FFDDDD" if is_cur else MED_TXT

        row = tk.Frame(self._tinner, bg=bg, cursor="hand2", bd=1, relief=tk.SOLID)
        row.pack(fill=tk.X, padx=4, pady=2)
        row._idx = idx

        th_lbl = tk.Label(row, bg=bg, width=50, height=48)
        th_lbl.pack(side=tk.LEFT, padx=4, pady=2)

        if idx in self._thumb_cache:
            th_lbl.config(image=self._thumb_cache[idx])
        elif trk.get("art"):
            ph = ImageTk.PhotoImage(make_thumb(trk["art"]).convert("RGBA"))
            self._thumb_cache[idx] = ph
            th_lbl.config(image=ph)
        else:
            dimg = default_art(size=44, bg="#C8A060" if rn%2==0 else "#B89050", fg=RED_DARK)
            ph   = ImageTk.PhotoImage(dimg.convert("RGB"))
            self._thumb_cache[idx] = ph
            th_lbl.config(image=ph)

        tf = tk.Frame(row, bg=bg)
        tf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        title_txt = trk["title"][:22] + "..." if len(trk["title"]) > 22 else trk["title"]
        tk.Label(tf, text=title_txt, font=("Arial", 9, "bold"),
                 fg=fg, bg=bg, anchor="w").pack(fill=tk.X)
        tk.Label(tf, text=trk["artist"][:22], font=("Arial", 8),
                 fg=fg2, bg=bg, anchor="w").pack(fill=tk.X)
        tk.Label(row, text=fmt_time(trk["dur"]), font=("Courier New", 9, "bold"),
                 fg=fg2, bg=bg, width=5).pack(side=tk.RIGHT, padx=6)

        for w in [row, th_lbl, tf] + list(tf.winfo_children()):
            w.bind("<Button-1>", lambda e, i=idx: self._click_track(i))
        self._track_rows.append(row)

    def _highlight_cur(self):
        for rn, row in enumerate(self._track_rows):
            idx    = row._idx
            is_cur = (idx == self.current_idx)
            bg  = SEL_BG if is_cur else (BG_CREAM if rn%2==0 else BG_LIGHT)
            fg  = SEL_FG if is_cur else DARK_TXT
            fg2 = "#FFDDDD" if is_cur else MED_TXT
            try:
                row.config(bg=bg)
                for w in row.winfo_children():
                    w.config(bg=bg)
                    if isinstance(w, tk.Label):
                        w.config(fg=fg2)
                    elif isinstance(w, tk.Frame):
                        w.config(bg=bg)
                        for ww in w.winfo_children():
                            ww.config(bg=bg)
                            if isinstance(ww, tk.Label):
                                ff = fg if ww.cget("font") and "bold" in str(ww.cget("font")) else fg2
                                ww.config(fg=ff)
            except Exception:
                pass

    def _filter_list(self):
        q = self._search_var.get().strip().lower()
        if not q:
            self._render_rows()
        else:
            matched = [i for i, t in enumerate(self.playlist)
                       if q in t["title"].lower() or q in t["artist"].lower()]
            self._render_rows(matched)

    def _read_track(self, fp):
        base   = os.path.splitext(os.path.basename(fp))[0]
        title  = base
        artist = "Unknown Artist"
        dur    = 0.0
        art    = None
        try:
            if fp.lower().endswith(".mp3"):
                audio = MP3(fp, ID3=ID3)
                dur   = audio.info.length
                if audio.tags:
                    if "TIT2" in audio.tags: title  = str(audio.tags["TIT2"]).strip()
                    if "TPE1" in audio.tags: artist = str(audio.tags["TPE1"]).strip()
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            art = Image.open(io.BytesIO(tag.data)).convert("RGB")
                            break
            elif fp.lower().endswith(".wav"):
                audio = WAVE(fp)
                dur   = audio.info.length
        except Exception:
            pass
        return {"path": fp, "title": title, "artist": artist, "dur": dur, "art": art}

    def load_folder(self):
        folder = filedialog.askdirectory(title="Select Music Folder")
        if not folder: return

        self._loading = True          
        try:
            self.lbl_path.config(text=f"Folder: {folder[:25]}..."
                                 if len(folder) > 25 else f"Folder: {folder}")
            self.playlist.clear()
            self._thumb_cache.clear()

            files = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                            if f.lower().endswith((".mp3", ".wav"))])
            if not files:
                return

            for i, fp in enumerate(files):
                self.playlist.append(self._read_track(fp))
                if i % 5 == 0:
                    self.master.update()

            self._render_rows()
            self.lbl_count.config(text=f"{len(self.playlist)} tracks")
            if self.playlist:
                self._set_track(0)
        finally:
            self._loading = False     

    def _draw_seek(self, pct=None):
        if pct is not None: self._seek_pct = pct
        w = self.seekbar.winfo_width()
        if w < 4: return
        h   = self.seekbar.winfo_height()
        mid = h // 2
        self.seekbar.delete("all")
        self.seekbar.create_rectangle(0, mid-4, w, mid+4, fill=BG_LIGHT, outline=BORDER)
        fw = int(w * self._seek_pct)
        if fw > 0:
            self.seekbar.create_rectangle(0, mid-4, fw, mid+4, fill=RED_DARK, outline="")
        tx = max(10, min(fw, w-10))
        self.seekbar.create_oval(tx-8, mid-8, tx+8, mid+8,
                                 fill=RED_DARK, outline=BG_CREAM, width=2)

    def _pct_from_event(self, event):
        w = self.seekbar.winfo_width()
        if w < 1: return 0.0
        return max(0.0, min(1.0, event.x / w))

    def _seek_press(self, event):
        self._dragging_seek = True
        self._draw_seek(self._pct_from_event(event))

    def _seek_drag(self, event):
        if self._dragging_seek:
            self._draw_seek(self._pct_from_event(event))

    def _seek_release(self, event):
        if not self._dragging_seek: return
        self._dragging_seek = False
        pct = self._pct_from_event(event)
        self._draw_seek(pct)
        with self._lock:
            tl = self.track_len
        if tl > 0:
            target = pct * tl
            self._play_offset = target
            try:
                pygame.mixer.music.play(start=target)
            except Exception:
                pygame.mixer.music.set_pos(target)

    def skip_time(self, seconds):
        if not self.is_playing: return
        with self._lock:
            tl = self.track_len
        if tl <= 0: return
        current_pos = self._play_offset + (pygame.mixer.music.get_pos() / 1000.0)
        new_pos     = max(0, min(current_pos + seconds, tl - 1))
        self._play_offset = new_pos
        self._draw_seek(new_pos / tl)
        try:
            pygame.mixer.music.play(start=new_pos)
        except Exception:
            pygame.mixer.music.set_pos(new_pos)

    def _set_track(self, idx):
        if not (0 <= idx < len(self.playlist)): return
        self.current_idx = idx
        trk = self.playlist[idx]
        with self._lock:
            self.track_len = trk["dur"]

        t = trk["title"][:28] + ("..." if len(trk["title"]) > 28 else "")
        self.lbl_title.config(text=t)
        self.lbl_artist.config(text=f"Artist: {trk['artist']}")
        ext = os.path.splitext(trk["path"])[1].upper().lstrip(".")
        self.lbl_type.config(text=f"Format: {ext}")
        self.lbl_total.config(text=fmt_time(trk["dur"]))
        self.lbl_cur.config(text="0:00")
        self._draw_seek(0.0)

        if trk["art"]:
            self._set_large_art(trk["art"])
            mini_pil = make_thumb(trk["art"], size=72)
            self._mini_art_photo = ImageTk.PhotoImage(mini_pil.convert("RGB"))
        else:
            self._show_default_large_art()
            self._mini_art_photo = None

        self._highlight_cur()
        self.lbl_ticker.config(text=f"  ♪ {trk['title']} — {trk['artist']}  ")

    def _play_music(self):
        if self.current_idx < 0: return
        try:
            trk = self.playlist[self.current_idx]
            pygame.mixer.music.load(trk["path"])
            self._play_offset = 0.0
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused  = False
            self._was_busy  = True
            self.btn_play.config(text="⏸ PAUSE", bg=WHITE, fg=RED_DARK)
        except Exception as e:
            print(f"[play error] {e}")

    def _click_track(self, idx):
        self._set_track(idx)
        self._play_music()

    def toggle_play(self):
        if self.current_idx < 0:
            if self.playlist:
                self._set_track(0)
                self._play_music()
            return
        if not self.is_playing:
            self._play_music()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_play.config(text="⏸ PAUSE", bg=WHITE, fg=RED_DARK)
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_play.config(text="▶ PLAY", bg=RED_DARK, fg=WHITE)

    def next_track(self):
        if not self.playlist: return
        if self.repeat_mode == 2:
            self._play_music(); return
        nxt = random.randint(0, len(self.playlist)-1) if self.is_shuffle \
              else (self.current_idx + 1) % len(self.playlist)
        self._set_track(nxt)
        self._play_music()

    def prev_track(self):
        if not self.playlist: return
        prv = random.randint(0, len(self.playlist)-1) if self.is_shuffle \
              else (self.current_idx - 1) % len(self.playlist)
        self._set_track(prv)
        self._play_music()

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.btn_shuffle.config(
            bg=RED_DARK if self.is_shuffle else BG_LIGHT,
            fg=WHITE    if self.is_shuffle else DARK_TXT)

    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        icons = ["🔁 Off", "🔁 All", "🔂 One"]
        on = self.repeat_mode > 0
        self.btn_repeat.config(text=icons[self.repeat_mode],
                               bg=RED_DARK if on else BG_LIGHT,
                               fg=WHITE    if on else DARK_TXT)

    def _on_vol(self, val):
        pygame.mixer.music.set_volume(float(val) / 100.0)
        self.lbl_vol.config(text=f"{int(float(val))}%")

    def _toggle_mini(self):
        if self.mini and self.mini.winfo_exists():
            self.close_mini()
        else:
            self.master.withdraw()
            self.mini = MiniPlayer(self.master, self)

    def close_mini(self):
        if self.mini and self.mini.winfo_exists():
            self.mini.destroy()
        self.mini = None
        self.master.deiconify()

    def _show_tutorial(self):
        TutorialWindow(self.master, lambda: None)

    def _poll_pygame_events(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.next_track()

    def _tick(self):
        try:
            self._integrity_guard()
            self._poll_pygame_events()
            with self._lock:
                tl = self.track_len

            if self.is_playing and not self.is_paused:
                busy = pygame.mixer.music.get_busy()
                if busy and tl > 0 and not self._dragging_seek:
                    pos = self._play_offset + (pygame.mixer.music.get_pos() / 1000.0)
                    if pos >= 0:
                        pct = min(pos / tl, 1.0)
                        self._draw_seek(pct)
                        self.lbl_cur.config(text=fmt_time(pos))
                        if self.mini and self.mini.winfo_exists():
                            trk = self.playlist[self.current_idx] \
                                  if 0 <= self.current_idx < len(self.playlist) else None
                            if trk:
                                self.mini.update_all(
                                    trk["title"], trk["artist"],
                                    self._mini_art_photo,
                                    "⏸" if not self.is_paused else "▶",
                                    fmt_time(pos), fmt_time(tl), pct)

            self._tick_count += 1
            if self._tick_count % 5 == 0:   
                self.lbl_master.config(text=SYSTEM_VOLUME)

        except tk.TclError:
            return
        self.master.after(200, self._tick)

if __name__ == "__main__":
    root = tk.Tk()
    app  = MusicPlayerApp(root)
    root.mainloop()