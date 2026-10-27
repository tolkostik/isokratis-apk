"""
Συνθετική ανθρώπινη φωνή για ισοκράτημα (καθαρή Python).

Κάθε νότα: κυματομορφή ενός κύκλου από αρμονικές που φιλτράρονται με τις
συχνότητες συντονισμού (formants) του φωνήεντος. Πάνω της προστίθενται μικρό, ακανόνιστο
τρέμουλο (vibrato), αργή διακύμανση έντασης, θόρυβος αναπνοής και, προαιρετικά,
τρεις ελαφρά διαφορετικές φωνές (χορωδία). Το αποτέλεσμα γίνεται βρόχος χωρίς ραφή.
"""
import array
import math
import random

SR = 16000          # Hz, αρκετό για ανδρική φωνή ισοκρατήματος
LOOP_SEC = 3.2
XFADE_SEC = 0.6
TABLE = 2048

VOWELS = {
    "Ο (στρογγυλό)": [(500, 90, 1.0), (850, 110, 0.45), (2400, 180, 0.12), (3300, 250, 0.05)],
    "Α (ανοιχτό)": [(730, 100, 1.0), (1090, 120, 0.55), (2440, 180, 0.25), (3400, 250, 0.08)],
    "Ου (κλειστό)": [(320, 70, 1.0), (800, 100, 0.28), (2240, 170, 0.07), (3200, 250, 0.03)],
    "Μμ (σιγοψάλσιμο)": [(250, 60, 1.0), (1050, 220, 0.05), (2200, 260, 0.02), (3000, 300, 0.01)],
}
DEFAULT_VOWEL = "Ο (στρογγυλό)"


def wavetable(f0, vowel):
    formants = VOWELS.get(vowel, VOWELS[DEFAULT_VOWEL])
    kmax = max(1, int(min(SR * 0.45, 5200) / f0))
    rnd = random.Random(int(f0 * 10))
    amps, phases = [], []
    for k in range(1, kmax + 1):
        fk = k * f0
        env = 0.0
        for F, B, g in formants:
            x = (fk - F) / (B / 2)
            env += g / (1 + x * x)
        a = (env + 0.015) * k ** -0.6       # κλίση φάσματος φωνητικών χορδών
        amps.append(a)
        phases.append(rnd.random() * 2 * math.pi)
    tab = [0.0] * TABLE
    w = 2 * math.pi / TABLE
    for k, (a, ph) in enumerate(zip(amps, phases), 1):
        if a < 1e-4:
            continue
        for i in range(TABLE):
            tab[i] += a * math.sin(k * w * i + ph)
    peak = max(abs(x) for x in tab) or 1.0
    return [x / peak for x in tab]


def render(f0, vowel=DEFAULT_VOWEL, chorus=True, seed=1):
    """Επιστρέφει bytes PCM 16-bit mono, βρόχος χωρίς ραφή."""
    rnd = random.Random(seed + int(f0 * 100))
    tab = wavetable(f0, vowel)
    loop_n = int(LOOP_SEC * SR)
    xf = int(XFADE_SEC * SR)
    n = loop_n + xf
    voices = [(0.0, 1.0)] if not chorus else [(0.0, 1.0), (4.0, 0.7), (-5.0, 0.7)]
    out = [0.0] * n
    block = 32
    for detune_cents, gain in voices:
        base = f0 * 2 ** (detune_cents / 1200)
        inc0 = base * TABLE / SR
        vib_rate = rnd.uniform(4.6, 5.6)
        vib_depth = rnd.uniform(0.0010, 0.0018)     # ~2–3 cents
        drift_rate = rnd.uniform(0.07, 0.13)
        drift_depth = rnd.uniform(0.0006, 0.0012)
        amp_rate = rnd.uniform(0.18, 0.35)
        ph_v, ph_d, ph_a = rnd.random() * 6.28, rnd.random() * 6.28, rnd.random() * 6.28
        phase = rnd.random() * TABLE
        jitter = 0.0
        for start in range(0, n, block):
            t = start / SR
            jitter = 0.98 * jitter + 0.02 * rnd.uniform(-1, 1)
            mod = (1 + vib_depth * math.sin(2 * math.pi * vib_rate * t + ph_v)
                   + drift_depth * math.sin(2 * math.pi * drift_rate * t + ph_d) + 0.0008 * jitter)
            inc = inc0 * mod
            amp = gain * (1 + 0.04 * math.sin(2 * math.pi * amp_rate * t + ph_a))
            end = min(n, start + block)
            for i in range(start, end):
                ip = int(phase)
                frac = phase - ip
                a = tab[ip & (TABLE - 1)]
                b = tab[(ip + 1) & (TABLE - 1)]
                out[i] += amp * (a + (b - a) * frac)
                phase += inc
                if phase >= TABLE:
                    phase -= TABLE
    # αναπνοή: χαμηλοπερατός θόρυβος, διαμορφωμένος από την κυματομορφή
    lp = 0.0
    breath = 0.035 * (len(voices) ** 0.5)
    for i in range(n):
        lp += 0.12 * (rnd.uniform(-1, 1) - lp)
        out[i] += breath * lp * (0.6 + 0.4 * abs(out[i]) / (len(voices)))
    # βρόχος χωρίς ραφή: το τέλος περνά ομαλά στην αρχή
    y = out[:loop_n]
    for i in range(xf):
        w = i / xf
        y[i] = out[i] * w + out[loop_n + i] * (1 - w)
    peak = max(abs(v) for v in y) or 1.0
    scale = 0.55 * 32767 / peak
    pcm = array.array("h", (int(v * scale) for v in y))
    return pcm.tobytes()


def to_wav(pcm, path):
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)
