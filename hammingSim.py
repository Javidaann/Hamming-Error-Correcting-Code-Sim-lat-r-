"""
BLM230 Bilgisayar Mimarisi - Dönem Projesi
Hamming Error-Correcting Code Simülatörü
=========================================
Desteklenen veri uzunlukları: 8, 16, 32 bit
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random


# ─────────────────────────────────────────
#  HAMMING CORE LOGIC
# ─────────────────────────────────────────

def calc_parity_bit_count(m: int) -> int:
    """Kaç tane parity biti gerektiğini hesaplar: 2^r >= m + r + 1"""
    r = 0
    while (1 << r) < (m + r + 1):
        r += 1
    return r


def encode(data_bits: list[int]) -> list[int]:
    """
    Veri bitlerini Hamming koduna çevirir.
    Giriş : data_bits  → [0,1,1,0,...] uzunluk m
    Çıkış : codeword   → 1-indexed liste (index 0 boş), uzunluk m+r
    """
    m = len(data_bits)
    r = calc_parity_bit_count(m)
    total = m + r

    # 1-indexed codeword dizisi (index 0 kullanılmaz)
    cw = [0] * (total + 1)

    # Veri bitlerini parity olmayan konumlara yerleştir
    di = 0
    for i in range(1, total + 1):
        if (i & (i - 1)) != 0:   # 2'nin kuvveti değilse → veri biti
            cw[i] = data_bits[di]
            di += 1

    # Her parity bitini hesapla
    for i in range(r):
        p = 1 << i          # 1, 2, 4, 8, ...
        xor_val = 0
        for j in range(1, total + 1):
            if j & p:       # j, p bitini içeriyorsa
                xor_val ^= cw[j]
        cw[p] = xor_val

    return cw  # 1-indexed


def calculate_syndrome(word: list[int]) -> tuple[int, list[dict]]:
    """
    Kod kelimesinin sendromunu hesaplar.
    Dönüş: (syndrome_value, parity_detail_list)
    syndrome == 0  → hata yok
    syndrome != 0  → hatalı bit konumu = syndrome
    """
    total = len(word) - 1   # index 0 boş
    m_guess = total
    r = 0
    while (1 << r) <= total:
        r += 1
    # Gerçek r değerini bul
    r = calc_parity_bit_count(total - r + 1 if total >= r else total)

    syndrome = 0
    details = []
    for i in range(r):
        p = 1 << i
        if p > total:
            break
        xor_val = 0
        covered = []
        for j in range(1, total + 1):
            if j & p:
                xor_val ^= word[j]
                covered.append(j)
        syndrome += xor_val * p
        details.append({"p": p, "val": xor_val, "covered": covered})

    return syndrome, details


def correct(word: list[int], syndrome: int) -> list[int]:
    """Hatalı biti düzeltir (kopyası üzerinde çalışır)."""
    corrected = word[:]
    if 0 < syndrome < len(corrected):
        corrected[syndrome] ^= 1
    return corrected


# ─────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────

COLORS = {
    "bg":         "#0f0f13",
    "surface":    "#1a1a24",
    "surface2":   "#22222f",
    "border":     "#2e2e42",
    "accent":     "#7c6af7",
    "accent2":    "#4ecdc4",
    "data_bit":   "#2d3b4e",
    "data_fg":    "#a8d8f0",
    "parity_bit": "#2d2d50",
    "parity_fg":  "#a09ef7",
    "error_bit":  "#4e1f1f",
    "error_fg":   "#f5a0a0",
    "fixed_bit":  "#1f3e2a",
    "fixed_fg":   "#7dd4a0",
    "text":       "#e8e8f0",
    "muted":      "#7a7a9a",
    "success":    "#4ade80",
    "danger":     "#f87171",
    "warn":       "#fbbf24",
}

FONT_TITLE  = ("Courier New", 15, "bold")
FONT_MONO   = ("Courier New", 11)
FONT_MONO_S = ("Courier New", 9)
FONT_BODY   = ("Courier New", 10)
FONT_LABEL  = ("Courier New", 9)


class HammingSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLM230 — Hamming ECC Simülatörü")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.minsize(820, 640)

        # State
        self.codeword: list[int] = []
        self.error_word: list[int] = []
        self.error_pos: int = -1
        self.bit_buttons: list[tk.Button] = []
        self.data_len: int = 8

        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w, h = 900, 700
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── UI Construction ──────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["bg"])
        hdr.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(hdr, text="◈ HAMMING ECC SİMÜLATÖRÜ",
                 font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["accent"]).pack(side="left")
        tk.Label(hdr, text="BLM230 Bilgisayar Mimarisi",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="right", pady=4)

        sep = tk.Frame(self, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(0, 12))

        # Main scroll canvas
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        canvas = tk.Canvas(outer, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        f = self.scroll_frame

        # Step 1 — Input
        self._section(f, "[ 1 ]  VERİ GİRİŞİ")
        inp = self._card(f)
        self._build_input_section(inp)

        # Step 2 — Encoded
        self._section(f, "[ 2 ]  KODLANMIŞ VERİ  (bellekte saklanan)")
        self.enc_card = self._card(f)
        self.enc_placeholder = tk.Label(self.enc_card,
            text="Henüz kodlanmamış. Veri girip 'Kodla' butonuna basın.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.enc_placeholder.pack(pady=12)

        # Step 3 — Error injection
        self._section(f, "[ 3 ]  HATA SİMÜLASYONU  (bite tıkla → hata ekle/kaldır)")
        self.err_card = self._card(f)
        self.err_placeholder = tk.Label(self.err_card,
            text="Önce veriyi kodlayın.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.err_placeholder.pack(pady=12)

        # Step 4 — Syndrome & Correction
        self._section(f, "[ 4 ]  SENDROM ANALİZİ & HATA DÜZELTME")
        self.syn_card = self._card(f)
        self.syn_placeholder = tk.Label(self.syn_card,
            text="Sendrom hesaplanmadı.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.syn_placeholder.pack(pady=12)

    def _section(self, parent, title):
        frm = tk.Frame(parent, bg=COLORS["bg"])
        frm.pack(fill="x", pady=(10, 2))
        tk.Label(frm, text=title, font=FONT_LABEL,
                 bg=COLORS["bg"], fg=COLORS["accent2"]).pack(side="left")

    def _card(self, parent):
        card = tk.Frame(parent, bg=COLORS["surface"],
                        relief="flat", bd=0,
                        highlightthickness=1,
                        highlightbackground=COLORS["border"])
        card.pack(fill="x", pady=(0, 6))
        inner = tk.Frame(card, bg=COLORS["surface"])
        inner.pack(fill="both", expand=True, padx=14, pady=12)
        return inner

    def _build_input_section(self, parent):
        row1 = tk.Frame(parent, bg=COLORS["surface"])
        row1.pack(fill="x", pady=(0, 8))

        tk.Label(row1, text="Bit uzunluğu:", font=FONT_BODY,
                 bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")

        self.bit_len_var = tk.IntVar(value=8)
        for val in (8, 16, 32):
            rb = tk.Radiobutton(row1, text=f"{val} bit", variable=self.bit_len_var,
                                value=val, font=FONT_BODY,
                                bg=COLORS["surface"], fg=COLORS["text"],
                                selectcolor=COLORS["surface2"],
                                activebackground=COLORS["surface"],
                                activeforeground=COLORS["accent"],
                                command=self._on_bitlen_change)
            rb.pack(side="left", padx=10)

        row2 = tk.Frame(parent, bg=COLORS["surface"])
        row2.pack(fill="x", pady=(0, 8))

        tk.Label(row2, text="İkili veri:", font=FONT_BODY,
                 bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")

        self.data_entry = tk.Entry(row2, font=FONT_MONO, width=36,
                                   bg=COLORS["surface2"], fg=COLORS["data_fg"],
                                   insertbackground=COLORS["accent"],
                                   relief="flat", bd=4,
                                   highlightthickness=1,
                                   highlightbackground=COLORS["border"],
                                   highlightcolor=COLORS["accent"])
        self.data_entry.pack(side="left", padx=(8, 6))

        self._btn(row2, "Rastgele", self._random_data, COLORS["surface2"])
        self._btn(row2, "Kodla  →", self._encode, COLORS["accent"])

        self.input_msg = tk.Label(parent, text="", font=FONT_BODY,
                                  bg=COLORS["surface"], fg=COLORS["danger"])
        self.input_msg.pack(anchor="w")

    def _btn(self, parent, text, cmd, bg=None, **kw):
        bg = bg or COLORS["surface2"]
        b = tk.Button(parent, text=text, command=cmd,
                      font=FONT_BODY, bg=bg, fg=COLORS["text"],
                      activebackground=COLORS["accent"],
                      activeforeground="#fff",
                      relief="flat", bd=0, padx=12, pady=5,
                      cursor="hand2", **kw)
        b.pack(side="left", padx=3)
        return b

    # ── Logic Handlers ───────────────────

    def _on_bitlen_change(self):
        self.data_entry.delete(0, "end")
        self.input_msg.config(text="")

    def _random_data(self):
        n = self.bit_len_var.get()
        bits = "".join(str(random.randint(0, 1)) for _ in range(n))
        self.data_entry.delete(0, "end")
        self.data_entry.insert(0, bits)
        self.input_msg.config(text="")

    def _encode(self):
        raw = self.data_entry.get().strip()
        n = self.bit_len_var.get()
        self.data_len = n

        if not all(c in "01" for c in raw):
            self.input_msg.config(text="⚠ Sadece 0 ve 1 kullanın.")
            return
        if len(raw) != n:
            self.input_msg.config(text=f"⚠ Tam {n} bit giriniz (şu an {len(raw)} bit).")
            return
        self.input_msg.config(text="")

        data_bits = [int(c) for c in raw]
        self.codeword = encode(data_bits)
        self.error_word = self.codeword[:]
        self.error_pos = -1

        self._render_encoded()
        self._render_error_section()
        self._clear_section(self.syn_card)
        self.syn_placeholder = tk.Label(self.syn_card,
            text="Hata ekledikten sonra 'Sendromu Hesapla' butonuna basın.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.syn_placeholder.pack(pady=12)

    def _clear_section(self, card):
        for w in card.winfo_children():
            w.destroy()

    def _render_encoded(self):
        self._clear_section(self.enc_card)
        cw = self.codeword
        total = len(cw) - 1
        r = calc_parity_bit_count(self.data_len)

        # Stats row
        stats = tk.Frame(self.enc_card, bg=COLORS["surface"])
        stats.pack(fill="x", pady=(0, 10))
        for label, val in [
            ("Veri bitleri", self.data_len),
            ("Parity bitleri", r),
            ("Toplam uzunluk", total),
        ]:
            box = tk.Frame(stats, bg=COLORS["surface2"],
                           highlightthickness=1, highlightbackground=COLORS["border"])
            box.pack(side="left", padx=(0, 8), pady=2)
            tk.Label(box, text=label, font=FONT_LABEL,
                     bg=COLORS["surface2"], fg=COLORS["muted"]).pack(padx=10, pady=(4, 0))
            tk.Label(box, text=str(val), font=FONT_MONO,
                     bg=COLORS["surface2"], fg=COLORS["text"]).pack(padx=10, pady=(0, 4))

        # Codeword string
        cw_str = "".join(str(cw[i]) for i in range(1, total + 1))
        tk.Label(self.enc_card, text=f"Kod kelimesi: {cw_str}",
                 font=FONT_MONO, bg=COLORS["surface"], fg=COLORS["accent2"]).pack(anchor="w", pady=(0, 6))

        # Bit grid
        self._render_bit_grid(self.enc_card, cw, total, mode="encoded")

        # Parity detail
        sep = tk.Frame(self.enc_card, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=8)
        tk.Label(self.enc_card, text="Parity bit hesabı:",
                 font=FONT_LABEL, bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        for i in range(r):
            p = 1 << i
            covered = [j for j in range(1, total + 1) if j & p]
            txt = (f"  P{p:>2}  (bit {p:>2}) → kapsar [{', '.join(map(str,covered))}]"
                   f"  →  değer = {cw[p]}")
            tk.Label(self.enc_card, text=txt, font=FONT_MONO_S,
                     bg=COLORS["surface"], fg=COLORS["parity_fg"]).pack(anchor="w")

        # Legend
        leg = tk.Frame(self.enc_card, bg=COLORS["surface"])
        leg.pack(anchor="w", pady=(8, 0))
        for color, label in [(COLORS["parity_fg"], "Parity biti"),
                              (COLORS["data_fg"],   "Veri biti")]:
            dot = tk.Label(leg, text="●", font=FONT_BODY, bg=COLORS["surface"], fg=color)
            dot.pack(side="left")
            tk.Label(leg, text=f" {label}   ", font=FONT_LABEL,
                     bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")

    def _render_bit_grid(self, parent, word, total, mode="encoded",
                         error_pos=-1, corrected=False):
        grid_frame = tk.Frame(parent, bg=COLORS["surface"])
        grid_frame.pack(fill="x", pady=4)

        cols = min(total, 32)
        for i in range(1, total + 1):
            is_parity = (i & (i - 1)) == 0
            is_err = (i == error_pos)

            if mode == "corrected" and is_err and corrected:
                bg, fg = COLORS["fixed_bit"], COLORS["fixed_fg"]
            elif is_err:
                bg, fg = COLORS["error_bit"], COLORS["error_fg"]
            elif is_parity:
                bg, fg = COLORS["parity_bit"], COLORS["parity_fg"]
            else:
                bg, fg = COLORS["data_bit"], COLORS["data_fg"]

            col_idx = (i - 1) % cols
            row_idx = (i - 1) // cols * 2

            # Position label
            pos_lbl = tk.Label(grid_frame, text=str(i), font=FONT_LABEL,
                                bg=COLORS["surface"], fg=COLORS["muted"], width=3)
            pos_lbl.grid(row=row_idx, column=col_idx, padx=2, pady=(2, 0))

            # Bit value
            bit_lbl = tk.Label(grid_frame, text=str(word[i]), font=FONT_MONO,
                                bg=bg, fg=fg, width=3, height=1,
                                relief="flat", bd=1)
            bit_lbl.grid(row=row_idx + 1, column=col_idx, padx=2, pady=(0, 4))

        return grid_frame

    def _render_error_section(self):
        self._clear_section(self.err_card)
        self.bit_buttons = []
        cw = self.codeword
        total = len(cw) - 1
        self.error_word = cw[:]
        self.error_pos = -1

        tk.Label(self.err_card,
                 text="Bir bite tıklayarak yapay hata oluşturun (tek seferde 1 bit):",
                 font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 6))

        grid_frame = tk.Frame(self.err_card, bg=COLORS["surface"])
        grid_frame.pack(anchor="w")

        cols = min(total, 32)
        self.err_buttons = []
        for i in range(1, total + 1):
            is_parity = (i & (i - 1)) == 0
            col_idx = (i - 1) % cols
            row_idx = (i - 1) // cols * 2

            pos_lbl = tk.Label(grid_frame, text=str(i), font=FONT_LABEL,
                                bg=COLORS["surface"], fg=COLORS["muted"], width=3)
            pos_lbl.grid(row=row_idx, column=col_idx, padx=2, pady=(2, 0))

            bg = COLORS["parity_bit"] if is_parity else COLORS["data_bit"]
            fg = COLORS["parity_fg"] if is_parity else COLORS["data_fg"]

            btn = tk.Button(grid_frame, text=str(cw[i]), font=FONT_MONO,
                            bg=bg, fg=fg, width=3, height=1,
                            relief="flat", bd=1, cursor="hand2",
                            activebackground=COLORS["error_bit"],
                            activeforeground=COLORS["error_fg"])
            btn.configure(command=lambda pos=i, b=btn, par=is_parity: self._toggle_error(pos, b, par))
            btn.grid(row=row_idx + 1, column=col_idx, padx=2, pady=(0, 4))
            self.err_buttons.append((i, btn, is_parity))

        # Info label
        self.error_info_lbl = tk.Label(self.err_card, text="",
                                        font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["warn"])
        self.error_info_lbl.pack(anchor="w", pady=(6, 4))

        # Detect button
        sep = tk.Frame(self.err_card, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=6)
        self._btn(self.err_card, "Sendromu Hesapla & Hatayı Tespit Et  →",
                  self._detect_error, COLORS["accent"])

    def _toggle_error(self, pos, btn, is_parity):
        if self.error_pos == pos:
            # Hata geri al
            self.error_word[pos] = self.codeword[pos]
            self.error_pos = -1
            bg = COLORS["parity_bit"] if is_parity else COLORS["data_bit"]
            fg = COLORS["parity_fg"] if is_parity else COLORS["data_fg"]
            btn.configure(bg=bg, fg=fg, text=str(self.error_word[pos]))
            self.error_info_lbl.config(text="")
        else:
            if self.error_pos != -1:
                messagebox.showinfo("Uyarı",
                    "Önce mevcut hatayı kaldırın (aynı bite tekrar tıklayın).")
                return
            self.error_pos = pos
            self.error_word[pos] ^= 1
            btn.configure(bg=COLORS["error_bit"], fg=COLORS["error_fg"],
                          text=str(self.error_word[pos]))
            self.error_info_lbl.config(
                text=f"⚡ Hata eklendi → Bit {pos}:  {self.codeword[pos]}  →  {self.error_word[pos]}")

    def _detect_error(self):
        self._clear_section(self.syn_card)
        syndrome, details = calculate_syndrome(self.error_word)
        total = len(self.error_word) - 1

        # Syndrome bits display
        tk.Label(self.syn_card, text="Sendrom bitleri:",
                 font=FONT_LABEL, bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")

        syn_frame = tk.Frame(self.syn_card, bg=COLORS["surface"])
        syn_frame.pack(anchor="w", pady=4)
        for d in details:
            color = COLORS["error_fg"] if d["val"] else COLORS["parity_fg"]
            txt = f"  P{d['p']:>2}: {d['val']}   (kapsar: {d['covered']})"
            tk.Label(syn_frame, text=txt, font=FONT_MONO_S,
                     bg=COLORS["surface"], fg=color).pack(anchor="w")

        sep = tk.Frame(self.syn_card, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=8)

        # Result
        if syndrome == 0:
            result_color = COLORS["success"]
            result_txt = "✓ SENDROM = 0 — Hata yok, veri bütünlüğü korunuyor."
        else:
            result_color = COLORS["danger"]
            result_txt = f"✗ SENDROM = {syndrome} — Bit {syndrome} hatalı!"

        tk.Label(self.syn_card, text=f"Sendrom değeri: {syndrome}",
                 font=FONT_MONO, bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(self.syn_card, text=result_txt,
                 font=FONT_MONO, bg=COLORS["surface"], fg=result_color).pack(anchor="w", pady=4)

        # Confirmation
        if self.error_pos > 0:
            if syndrome == self.error_pos:
                conf = f"✓ TEYİT: Yapay hata bit {self.error_pos}'deydi — sendrom doğru gösterdi."
                conf_color = COLORS["success"]
            else:
                conf = f"✗ UYUMSUZLUK: Beklenen bit {self.error_pos}, sendrom bit {syndrome} gösteriyor."
                conf_color = COLORS["danger"]
            tk.Label(self.syn_card, text=conf, font=FONT_BODY,
                     bg=COLORS["surface"], fg=conf_color).pack(anchor="w")

        # Corrected word
        if syndrome != 0:
            sep2 = tk.Frame(self.syn_card, bg=COLORS["border"], height=1)
            sep2.pack(fill="x", pady=8)
            corrected = correct(self.error_word, syndrome)
            tk.Label(self.syn_card,
                     text=f"Düzeltilmiş kod kelimesi (bit {syndrome} çevrildi):",
                     font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
            self._render_bit_grid(self.syn_card, corrected, total,
                                  mode="corrected", error_pos=syndrome, corrected=True)
            cw_str = "".join(str(corrected[i]) for i in range(1, total + 1))
            tk.Label(self.syn_card, text=f"Sonuç: {cw_str}",
                     font=FONT_MONO, bg=COLORS["surface"], fg=COLORS["accent2"]).pack(anchor="w", pady=4)

        # Reset button
        sep3 = tk.Frame(self.syn_card, bg=COLORS["border"], height=1)
        sep3.pack(fill="x", pady=8)
        self._btn(self.syn_card, "↺ Yeniden Başla", self._reset)

    def _reset(self):
        self.data_entry.delete(0, "end")
        self.codeword = []
        self.error_word = []
        self.error_pos = -1
        self._clear_section(self.enc_card)
        self.enc_placeholder = tk.Label(self.enc_card,
            text="Henüz kodlanmamış. Veri girip 'Kodla' butonuna basın.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.enc_placeholder.pack(pady=12)
        self._clear_section(self.err_card)
        self.err_placeholder = tk.Label(self.err_card,
            text="Önce veriyi kodlayın.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.err_placeholder.pack(pady=12)
        self._clear_section(self.syn_card)
        self.syn_placeholder = tk.Label(self.syn_card,
            text="Sendrom hesaplanmadı.",
            font=FONT_BODY, bg=COLORS["surface"], fg=COLORS["muted"])
        self.syn_placeholder.pack(pady=12)
        self.input_msg.config(text="")


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    app = HammingSimulator()
    app.mainloop()
