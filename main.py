"""
Ψηφιακός Ισοκράτης Βυζαντινής Μουσικής.
"""
import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import synth
import theory as T
from audio import Engine

Window.clearcolor = (0.055, 0.063, 0.082, 1)
AMBER = (0.95, 0.71, 0.14, 1)
DARK_BTN = (0.13, 0.15, 0.19, 1)
INK_LIGHT = (0.93, 0.9, 0.82, 1)
INK_DIM = (0.62, 0.64, 0.68, 1)
MAX_DRONES = 4

DEFAULTS = {
    "genus": "Διατονικό", "mode": "Ελεύθερα", "octave": "Μέση", "multi": False,
    "vowel": synth.DEFAULT_VOWEL, "chorus": True, "tempered": False,
    "attack": 0.6, "release": 1.2, "semis": 0, "moria": 0, "volume": 0.8,
    "alter": [0, 0, 0, 0, 0, 0, 0],
}

KV = """
#:import dp kivy.metrics.dp

<Dim@Label>:
    color: 0.62, 0.64, 0.68, 1
    font_size: '13sp'
    halign: 'left'
    valign: 'middle'
    text_size: self.size

<Flat@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0.13, 0.15, 0.19, 1
    color: 0.93, 0.9, 0.82, 1
    font_size: '15sp'

<Seg@ToggleButton>:
    background_normal: ''
    background_down: ''
    background_color: (0.95, 0.71, 0.14, 1) if self.state == 'down' else (0.13, 0.15, 0.19, 1)
    color: (0.06, 0.07, 0.09, 1) if self.state == 'down' else (0.93, 0.9, 0.82, 1)
    font_size: '15sp'
    bold: True

<DarkSpinner@Spinner>:
    background_normal: ''
    background_color: 0.13, 0.15, 0.19, 1
    color: 0.95, 0.71, 0.14, 1
    font_size: '15sp'
    option_cls: 'DarkOption'

<DarkOption@SpinnerOption>:
    background_normal: ''
    background_color: 0.1, 0.11, 0.14, 1
    color: 0.93, 0.9, 0.82, 1
    height: dp(48)

<NoteBtn>:
    background_normal: ''
    background_down: ''
    markup: True
    halign: 'center'
    background_color: self.bg
    color: self.fg

<Root>:
    orientation: 'vertical'
    ScreenManager:
        id: sm
        Screen:
            name: 'main'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(10), dp(8)
                spacing: dp(8)
                BoxLayout:
                    size_hint_y: None
                    height: dp(54)
                    Label:
                        text: 'Ισοκράτης'
                        bold: True
                        font_size: '22sp'
                        color: 0.95, 0.71, 0.14, 1
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.size
                    Label:
                        id: status
                        font_size: '12sp'
                        color: 0.62, 0.64, 0.68, 1
                        halign: 'right'
                        valign: 'middle'
                        text_size: self.size
                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(8)
                    DarkSpinner:
                        id: mode
                        on_text: app.set_mode(self.text)
                    DarkSpinner:
                        id: genus
                        on_text: app.set_genus(self.text)
                BoxLayout:
                    size_hint_y: None
                    height: dp(46)
                    spacing: dp(6)
                    Seg:
                        id: oct_low
                        text: 'Χαμηλά'
                        group: 'oct'
                        allow_no_selection: False
                        on_release: app.set_octave('Χαμηλά')
                    Seg:
                        id: oct_mid
                        text: 'Μέση'
                        group: 'oct'
                        allow_no_selection: False
                        on_release: app.set_octave('Μέση')
                    Seg:
                        id: oct_high
                        text: 'Ψηλά'
                        group: 'oct'
                        allow_no_selection: False
                        on_release: app.set_octave('Ψηλά')
                GridLayout:
                    id: grid
                    cols: 4
                    spacing: dp(8)
                BoxLayout:
                    size_hint_y: None
                    height: dp(46)
                    spacing: dp(6)
                    Seg:
                        id: single
                        text: 'Ένα'
                        group: 'multi'
                        allow_no_selection: False
                        on_release: app.set_multi(False)
                    Seg:
                        id: multi
                        text: 'Έως 4 μαζί'
                        group: 'multi'
                        allow_no_selection: False
                        on_release: app.set_multi(True)
                    Flat:
                        text: '+ 5η'
                        on_release: app.add_fifth()
                    Flat:
                        text: '+ 8η κάτω'
                        on_release: app.add_octave_below()
                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(8)
                    Dim:
                        text: 'Ένταση'
                        size_hint_x: None
                        width: dp(64)
                    Slider:
                        id: volume
                        min: 0
                        max: 1
                        value_track: True
                        value_track_color: 0.95, 0.71, 0.14, 1
                        on_value: app.set_volume(self.value)
                Button:
                    text: 'ΣΙΩΠΗ'
                    bold: True
                    font_size: '20sp'
                    size_hint_y: None
                    height: dp(62)
                    background_normal: ''
                    background_color: 0.45, 0.12, 0.1, 1
                    color: 1, 0.93, 0.88, 1
                    on_release: app.silence()
        Screen:
            name: 'settings'
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    id: settings
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(14), dp(10)
                    spacing: dp(8)
    BoxLayout:
        size_hint_y: None
        height: dp(52)
        Seg:
            id: nav_main
            text: 'Ισοκράτης'
            group: 'nav'
            state: 'down'
            allow_no_selection: False
            on_release: app.root_w.ids.sm.current = 'main'
        Seg:
            id: nav_set
            text: 'Ήχος & Φθορές'
            group: 'nav'
            allow_no_selection: False
            on_release: app.root_w.ids.sm.current = 'settings'
"""


class NoteBtn(Button):
    bg = ListProperty(list(DARK_BTN))
    fg = ListProperty(list(AMBER))


class Root(BoxLayout):
    pass


Builder.load_string(KV)


class IsokratisApp(App):
    title = "Isokratis"

    def build(self):
        self.cfg_path = os.path.join(self.user_data_dir, "settings.json")
        self.cfg = dict(DEFAULTS)
        try:
            with open(self.cfg_path, encoding="utf-8") as f:
                self.cfg.update(json.load(f))
        except Exception:  # noqa: BLE001
            pass
        self.engine = Engine(os.path.join(self.user_data_dir, "voices"))
        self.engine.master = self.cfg["volume"]
        self.engine.attack = self.cfg["attack"]
        self.engine.release = self.cfg["release"]
        self.active = []          # [(φθόγγος 0..7, οκτάβα -2..2)]
        self.root_w = Root()
        ids = self.root_w.ids
        self._loading = True
        ids.mode.values = ["Ελεύθερα"] + list(T.MODES)
        ids.mode.text = self.cfg["mode"]
        ids.genus.values = list(T.GENERA)
        ids.genus.text = self.cfg["genus"]
        ids.volume.value = self.cfg["volume"]
        {"Χαμηλά": ids.oct_low, "Μέση": ids.oct_mid, "Ψηλά": ids.oct_high}[self.cfg["octave"]].state = "down"
        (ids.multi if self.cfg["multi"] else ids.single).state = "down"
        self.note_btns = []
        for d in range(8):
            b = NoteBtn(font_size="26sp")
            b.bind(on_release=lambda w, deg=d: self.press(deg))
            ids.grid.add_widget(b)
            self.note_btns.append(b)
        self._build_settings(ids.settings)
        self._loading = False
        self.refresh()
        self.prefetch()
        return self.root_w

    def on_pause(self):
        return True       # ο ήχος συνεχίζει αν σβήσει η οθόνη

    # ------------------------------------------------------------ βοηθητικά
    def save(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.cfg_path, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, ensure_ascii=False)
        except OSError:
            pass

    def freq(self, d, o):
        c = self.cfg
        return T.frequency(d, o, c["genus"], c["semis"], c["moria"], c["tempered"], c["alter"])

    def key(self, d, o):
        return Engine.key_for(self.freq(d, o), self.cfg["vowel"], self.cfg["chorus"])

    def cur_octave(self):
        return T.OCTAVES[self.cfg["octave"]]

    def apply(self):
        self.engine.play([self.key(d, o) for d, o in self.active])
        self.refresh()

    def prefetch(self):
        o = self.cur_octave()
        self.engine.prefetch([self.key(d, o) for d in range(8)])

    def changed(self, prefetch=True):
        if self._loading:
            return
        self.save()
        self.apply()
        if prefetch:
            self.prefetch()

    # ------------------------------------------------------------ οθόνη
    def refresh(self):
        o = self.cur_octave()
        pos = T.positions(self.cfg["genus"], self.cfg["tempered"], self.cfg["alter"])
        for d, b in enumerate(self.note_btns):
            on = any(ad == d and ao == o for ad, ao in self.active)
            other = any(ad == d for ad, ao in self.active) and not on
            hz = self.freq(d, o)
            alt = self.cfg["alter"][d % 7]
            mark = f" [size=12sp]({alt:+d})[/size]" if alt else ""
            b.text = f"[b]{T.label(d)}[/b]{mark}\n[size=12sp]{hz:.1f} Hz[/size]".replace(".", ",")
            b.bg = list(AMBER) if on else ([0.25, 0.2, 0.08, 1] if other else list(DARK_BTN))
            b.fg = [0.06, 0.07, 0.09, 1] if on else list(AMBER)
        names = " + ".join(f"{T.label(d)}{'' if oo == 0 else (' χαμ.' if oo < 0 else ' ψηλ.')}"
                           for d, oo in self.active)
        base = T.base_name(self.cfg["semis"]) + (f" {self.cfg['moria']:+d} μ." if self.cfg["moria"] else "")
        scale = "συγκερασμένη" if self.cfg["tempered"] else "βυζαντινή"
        self.root_w.ids.status.text = (f"Νη = {base} · {scale}\n" + (f"Ηχεί: {names}" if names else "Σιωπή"))
        # τα διαστήματα του γένους
        pos7 = pos + [pos[0] + 72]
        steps = " ".join(str(b - a) for a, b in zip(pos7, pos7[1:]))
        if hasattr(self, "steps_lbl"):
            self.steps_lbl.text = f"Διαστήματα (μόρια) Νη→Νη': {steps}"

    # ------------------------------------------------------------ χειρισμός
    def press(self, d):
        o = self.cur_octave()
        item = (d, o)
        if self.cfg["multi"]:
            if item in self.active:
                self.active.remove(item)
            else:
                self.active.append(item)
                if len(self.active) > MAX_DRONES:
                    self.active.pop(0)
        else:
            self.active = [] if self.active == [item] else [item]
        self.apply()

    def add_fifth(self):
        if not self.active:
            return
        d, o = self.active[-1]
        if d == 7:
            d, o = 0, o + 1
        nd, no = d + 4, o
        if nd >= 7:
            nd, no = nd - 7, o + 1
        self._add((nd, no))

    def add_octave_below(self):
        if not self.active:
            return
        d, o = self.active[-1]
        self._add((d, o - 1))

    def _add(self, item):
        if not self.cfg["multi"]:
            self.cfg["multi"] = True
            self.root_w.ids.multi.state = "down"
            self.root_w.ids.single.state = "normal"
        if item not in self.active:
            self.active.append(item)
            if len(self.active) > MAX_DRONES:
                self.active.pop(0)
        self.changed(prefetch=False)

    def silence(self):
        self.active = []
        self.engine.stop_all()
        self.refresh()

    def set_mode(self, m):
        if self._loading:
            return
        self.cfg["mode"] = m
        if m in T.MODES:
            genus, deg = T.MODES[m]
            self.cfg["genus"] = genus
            self.root_w.ids.genus.text = genus
            self.active = [(deg, self.cur_octave())]
        self.changed()

    def set_genus(self, g):
        if self._loading or g not in T.GENERA:
            return
        self.cfg["genus"] = g
        self.changed()

    def set_octave(self, name):
        self.cfg["octave"] = name
        self.save()
        self.refresh()
        self.prefetch()

    def set_multi(self, on):
        self.cfg["multi"] = on
        if not on and len(self.active) > 1:
            self.active = self.active[-1:]
            self.apply()
        self.save()

    def set_volume(self, v):
        self.cfg["volume"] = float(v)
        self.engine.master = float(v)
        if not self._loading:
            self.save()

    # ------------------------------------------------------------ ρυθμίσεις
    def _build_settings(self, box):
        from kivy.factory import Factory

        def title(t):
            box.add_widget(Label(text=t, bold=True, font_size="17sp", color=AMBER, size_hint_y=None,
                                 height=dp(40), halign="left", valign="bottom",
                                 text_size=(Window.width - dp(28), None)))

        def line(label, widget, h=48):
            row = BoxLayout(size_hint_y=None, height=dp(h), spacing=dp(8))
            row.add_widget(Label(text=label, color=INK_LIGHT, halign="left", valign="middle",
                                 text_size=(Window.width * 0.4, None), size_hint_x=0.42))
            widget.size_hint_x = 0.58
            row.add_widget(widget)
            box.add_widget(row)
            return row

        def slider(label, mn, mx, val, step, fmt, cb):
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
            lab = Label(text=label + ": " + fmt(val), color=INK_LIGHT, halign="left", valign="middle",
                        text_size=(Window.width * 0.4, None), size_hint_x=0.42)
            s = Factory.Slider(min=mn, max=mx, value=val, step=step, size_hint_x=0.58, value_track=True,
                               value_track_color=AMBER)

            def on_val(w, v):
                lab.text = label + ": " + fmt(v)
                cb(v)
            s.bind(value=on_val)
            row.add_widget(lab)
            row.add_widget(s)
            box.add_widget(row)

        title("Φωνή")
        sp = Factory.DarkSpinner(text=self.cfg["vowel"], values=list(synth.VOWELS))
        sp.bind(text=lambda w, v: self._set("vowel", v))
        line("Χροιά", sp)
        ch = Factory.Seg(text="Χορωδία (3 φωνές)", state="down" if self.cfg["chorus"] else "normal")
        ch.bind(state=lambda w, st: self._set("chorus", st == "down"))
        line("Ήχος", ch)
        slider("Attack", 0.05, 3.0, self.cfg["attack"], 0.05, lambda v: f"{v:.2f} s".replace(".", ","),
               lambda v: self._env("attack", v))
        slider("Release", 0.05, 4.0, self.cfg["release"], 0.05, lambda v: f"{v:.2f} s".replace(".", ","),
               lambda v: self._env("release", v))

        title("Κλίμακα και τονικότητα")
        tp = Factory.Seg(text="Συγκερασμένη (ευρωπαϊκή)", state="down" if self.cfg["tempered"] else "normal")
        tp.bind(state=lambda w, st: self._set("tempered", st == "down"))
        line("Κλίμακα", tp)
        slider("Νη (ημιτόνια)", -12, 12, self.cfg["semis"], 1, lambda v: T.base_name(int(v)),
               lambda v: self._set("semis", int(v), delay=True))
        slider("Λεπτή ρύθμιση", -6, 6, self.cfg["moria"], 1, lambda v: f"{int(v):+d} μόρια",
               lambda v: self._set("moria", int(v), delay=True))
        self.steps_lbl = Label(text="", color=INK_DIM, font_size="13sp", size_hint_y=None, height=dp(30),
                               halign="left", valign="middle", text_size=(Window.width - dp(28), None))
        box.add_widget(self.steps_lbl)

        title("Φθορές και χρόες (αλλοίωση φθόγγων)")
        box.add_widget(Label(text="Ύφεση (−) ή δίεση (+) κάθε φθόγγου ανά 2 μόρια, πάνω στο γένος που "
                                  "έχεις διαλέξει.", color=INK_DIM, font_size="13sp", size_hint_y=None,
                             height=dp(40), halign="left", valign="middle",
                             text_size=(Window.width - dp(28), None)))
        self.alter_lbls = []
        for i, name in enumerate(T.NAMES):
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
            row.add_widget(Label(text=name, bold=True, font_size="18sp", color=AMBER, size_hint_x=0.25))
            minus = Factory.Flat(text="−", font_size="24sp", size_hint_x=0.22)
            lab = Label(text="", color=INK_LIGHT, font_size="16sp", size_hint_x=0.31)
            plus = Factory.Flat(text="+", font_size="24sp", size_hint_x=0.22)
            minus.bind(on_release=lambda w, k=i: self._alter(k, -2))
            plus.bind(on_release=lambda w, k=i: self._alter(k, +2))
            for w in (minus, lab, plus):
                row.add_widget(w)
            box.add_widget(row)
            self.alter_lbls.append(lab)
        reset = Factory.Flat(text="Μηδενισμός φθορών", size_hint_y=None, height=dp(48))
        reset.bind(on_release=lambda w: self._alter(None, 0))
        box.add_widget(reset)
        self._alter_labels()

        title("Έξοδοι ήχου")
        box.add_widget(Label(
            text=("• Ακουστικά / καλώδιο: από την έξοδο ήχου ή το USB-C (με αντάπτορα).\n"
                  "• Bluetooth: σύνδεσε το ηχείο από τις ρυθμίσεις του κινητού, ο ήχος πηγαίνει εκεί αυτόματα.\n"
                  "• Κονσόλα ναού (balanced XLR): από την έξοδο του κινητού σε DI box ή σε κάρτα ήχου USB, "
                  "και από εκεί με καλώδιο XLR στην κονσόλα, για ήχο χωρίς βόμβο.\n"
                  "• Η οθόνη μένει αναμμένη και ο ήχος συνεχίζει όσο η εφαρμογή είναι ανοιχτή."),
            color=INK_DIM, font_size="13sp", size_hint_y=None, height=dp(190), halign="left", valign="top",
            text_size=(Window.width - dp(28), None)))

    def _set(self, k, v, delay=False):
        if self.cfg.get(k) == v:
            return
        self.cfg[k] = v
        if delay:
            if getattr(self, "_job", None):
                self._job.cancel()
            self._job = Clock.schedule_once(lambda dt: self.changed(), 0.35)
            self.refresh()
        else:
            self.changed()

    def _env(self, k, v):
        self.cfg[k] = float(v)
        setattr(self.engine, k, float(v))
        self.save()

    def _alter(self, idx, delta):
        if idx is None:
            self.cfg["alter"] = [0] * 7
        else:
            a = list(self.cfg["alter"])
            a[idx] = max(-12, min(12, a[idx] + delta))
            self.cfg["alter"] = a
        self._alter_labels()
        self.changed()

    def _alter_labels(self):
        for i, lab in enumerate(self.alter_lbls):
            v = self.cfg["alter"][i]
            lab.text = "0" if v == 0 else (f"δίεση +{v}" if v > 0 else f"ύφεση {v}")


if __name__ == "__main__":
    IsokratisApp().run()
