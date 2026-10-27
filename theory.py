"""
Βυζαντινή θεωρία για τον ισοκράτη.

Οκτάβα 72 μορίων (Πατριαρχική Μουσική Επιτροπή, 1881).
Κάθε γένος ορίζεται από τον φθόγγο-βάση του (που μένει στη θέση του διατονικού)
και τα διαστήματα προς τα πάνω από αυτόν.
"""
NAMES = ["Νη", "Πα", "Βου", "Γα", "Δι", "Κε", "Ζω"]

DIATONIC_POS = [0, 12, 22, 30, 42, 54, 64]

GENERA = {
    # όνομα: (δείκτης φθόγγου-βάσης, διαστήματα από τη βάση προς τα πάνω)
    "Διατονικό": (0, [12, 10, 8, 12, 12, 10, 8]),
    "Χρωματικό μαλακό": (4, [8, 14, 8, 12, 8, 14, 8]),   # Β' ήχος, βάση Δι
    "Χρωματικό σκληρό": (1, [6, 20, 4, 12, 6, 20, 4]),   # Πλ. Β' ήχος, βάση Πα
    "Εναρμόνιο": (3, [12, 12, 6, 12, 12, 12, 6]),         # Γ' ήχος & Βαρύς, βάση Γα
}

# Ήχοι: (γένος, φθόγγος βάσης)
MODES = {
    "Α' ήχος (Πα)": ("Διατονικό", 1),
    "Β' ήχος (Δι)": ("Χρωματικό μαλακό", 4),
    "Γ' ήχος (Γα)": ("Εναρμόνιο", 3),
    "Δ' ήχος Άγια (Δι)": ("Διατονικό", 4),
    "Δ' ήχος Λέγετος (Βου)": ("Διατονικό", 2),
    "Πλ. Α' ήχος (Πα)": ("Διατονικό", 1),
    "Πλ. Α' ήχος (Κε)": ("Διατονικό", 5),
    "Πλ. Β' ήχος (Πα)": ("Χρωματικό σκληρό", 1),
    "Βαρύς ήχος (Γα)": ("Εναρμόνιο", 3),
    "Πλ. Δ' ήχος (Νη)": ("Διατονικό", 0),
}

NOTE_NAMES = ["Ντο", "Ντο#", "Ρε", "Μιb", "Μι", "Φα", "Φα#", "Σολ", "Λαb", "Λα", "Σιb", "Σι"]
C3 = 130.8128

OCTAVES = {"Χαμηλά": -1, "Μέση": 0, "Ψηλά": 1}


def positions(genus, tempered=False, alterations=None):
    """Θέση κάθε φθόγγου σε μόρια πάνω από τον Νη (0..72)."""
    anchor, steps = GENERA[genus]
    pos = [0] * 7
    cur = DIATONIC_POS[anchor]
    for k in range(7):
        idx = anchor + k
        p = cur
        if idx >= 7:
            p -= 72
        pos[idx % 7] = p
        cur += steps[k]
    alterations = alterations or [0] * 7
    pos = [p + a for p, a in zip(pos, alterations)]
    if tempered:
        pos = [6 * round(p / 6) for p in pos]
    return pos


def base_frequency(semitones=0, moria=0):
    """Συχνότητα του Νη (μέση περιοχή). Προεπιλογή: Νη = Ντο3."""
    return C3 * 2 ** (semitones / 12 + moria / 72)


def base_name(semitones):
    octave = 3 + (semitones // 12)
    return f"{NOTE_NAMES[semitones % 12]}{octave}"


def frequency(degree, octave, genus, semitones=0, moria=0, tempered=False, alterations=None):
    """degree: 0..7 (7 = Νη' πάνω), octave: -1/0/1."""
    pos = positions(genus, tempered, alterations)
    p = pos[degree % 7] + (72 if degree == 7 else 0)
    return base_frequency(semitones, moria) * 2 ** ((p + 72 * octave) / 72)


def label(degree):
    return "Νη'" if degree == 7 else NAMES[degree]
