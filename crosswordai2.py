import streamlit as st
import random

st.set_page_config(page_title="Cruciverba 24x14", layout="centered")

@st.cache_data
def prepara_dizionario():
    # Legge il file di testo riga per riga
    try:
        with open("parole.txt", "r", encoding="utf-8") as f:
            lines = [line.strip().upper() for line in f if len(line.strip()) >= 3]
        return sorted(list(set(lines)), key=len, reverse=True)
    except FileNotFoundError:
        return ["ERRORE", "FILE", "MANCANTE"]

# --- IL RESTO DELLE FUNZIONI RIMANE IDENTICO A PRIMA ---

# [Logica invariata]
def controlla_vincoli_spazio(griglia, parola, riga, col, direzione, R, C):
    lunghezza = len(parola)
    if direzione == "H":
        if col + lunghezza > C: return False
        if col > 0 and griglia[riga][col-1] != "◼": return False
        if col + lunghezza < C and griglia[riga][col+lunghezza] != "◼" and griglia[riga][col+lunghezza] != "": return False
        for i, char in enumerate(parola):
            c_corrente = col + i
            if griglia[riga][c_corrente] not in ["", "◼", char]: return False
            if griglia[riga][c_corrente] == "◼": return False
    else:
        if riga + lunghezza > R: return False
        if riga > 0 and griglia[riga-1][col] != "◼": return False
        if riga + lunghezza < R and griglia[riga+lunghezza][col] != "◼" and griglia[riga+lunghezza][col] != "": return False
        for i, char in enumerate(parola):
            r_corrente = riga + i
            if griglia[r_corrente][col] not in ["", "◼", char]: return False
            if griglia[r_corrente][col] == "◼": return False
    return True

def inserisci_parola_e_nere(griglia, parola, riga, col, direzione, R, C):
    for k, char in enumerate(parola):
        if direzione == "H": griglia[riga][col + k] = char
        else: griglia[riga + k][col] = char
    if direzione == "H":
        if col > 0: griglia[riga][col-1] = "◼"
        if col + len(parola) < C: griglia[riga][col+len(parola)] = "◼"
    else:
        if riga > 0: griglia[riga-1][col] = "◼"
        if riga + len(parola) < R: griglia[riga+len(parola)][col] = "◼"

def genera_griglia(R, C, dizionario):
    griglia = [["" for _ in range(C)] for _ in range(R)]
    pool = random.sample(dizionario, len(dizionario))
    piazzate = []
    
    # Prima parola
    p = pool.pop(0)
    inserisci_parola_e_nere(griglia, p, R//2, (C-len(p))//2, "H", R, C)
    piazzate.append({"parola": p, "direzione": "H", "riga": R//2, "col": (C-len(p))//2})
    
    for p in pool:
        for info in piazzate:
            for i, c1 in enumerate(p):
                for j, c2 in enumerate(info["parola"]):
                    if c1 == c2:
                        d = "V" if info["direzione"] == "H" else "H"
                        r = info["riga"] - i if d == "V" else info["riga"] + j
                        c = info["col"] + j if d == "V" else info["col"] - i
                        if 0 <= r < R and 0 <= c < C and controlla_vincoli_spazio(griglia, p, r, c, d, R, C):
                            inserisci_parola_e_nere(griglia, p, r, c, d, R, C)
                            piazzate.append({"parola": p, "direzione": d, "riga": r, "col": c})
                            break
                else: continue
                break
    return griglia

# UI
st.title("🧩 Cruciverba")
if st.button("Genera"):
    griglia = genera_griglia(14, 24, prepara_dizionario())
    html = '<table style="border-collapse: collapse; background:black;">'
    for r in griglia:
        html += '<tr>' + ''.join([f'<td style="width:25px;height:25px;background:{"white" if c != "◼" else "black"};border:1px solid #333;text-align:center;font-weight:bold;">{c if c!="◼" else ""}</td>' for c in r]) + '</tr>'
    st.markdown(html + '</table>', unsafe_allow_html=True)
