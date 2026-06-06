import streamlit as st
import random
import urllib.request

# --- Configurazioni della pagina ---
st.set_page_config(page_title="Cruciverba Python", layout="centered")

DICT_URL = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/paroleitaliane/parole_italiane.txt"

@st.cache_data(show_spinner="Scaricamento dizionario in corso...")
def carica_dizionario():
    """Scarica e mette in cache il dizionario per evitare download multipli."""
    try:
        response = urllib.request.urlopen(DICT_URL, timeout=5)
        words = response.read().decode('utf-8').splitlines()
        parole = [w.upper() for w in words if w.isalpha() and len(w) > 2]
    except Exception:
        # Fallback in caso di problemi di rete
        parole = ["ENIGMA", "PYTHON", "STREAMLIT", "GITHUB", "IPAD", "INFORMATICA", 
                  "GATTO", "CANE", "SOLE", "LUNA", "MARE", "VITA", "PROGRAMMAZIONE"]
    
    # Ordiniamo per lunghezza decrescente per favorire incroci con parole lunghe
    parole.sort(key=len, reverse=True)
    return parole

def controlla_spazio(griglia, parola, riga, col, direzione, R, C):
    """Verifica se la parola può essere inserita senza collisioni errate."""
    if direzione == "H":
        if col + len(parola) > C: return False
        if col > 0 and griglia[riga][col-1] != "": return False
        if col + len(parola) < C and griglia[riga][col+len(parola)] != "": return False
        
        for i, char in enumerate(parola):
            c_corrente = col + i
            if griglia[riga][c_corrente] != "" and griglia[riga][c_corrente] != char:
                return False
            if griglia[riga][c_corrente] == "":
                if riga > 0 and griglia[riga-1][c_corrente] != "": return False
                if riga < R-1 and griglia[riga+1][c_corrente] != "": return False
    else: # "V"
        if riga + len(parola) > R: return False
        if riga > 0 and griglia[riga-1][col] != "": return False
        if riga + len(parola) < R and griglia[riga+len(parola)][col] != "": return False
        
        for i, char in enumerate(parola):
            r_corrente = riga + i
            if griglia[r_corrente][col] != "" and griglia[r_corrente][col] != char:
                return False
            if griglia[r_corrente][col] == "":
                if col > 0 and griglia[r_corrente][col-1] != "": return False
                if col < C-1 and griglia[r_corrente][col+1] != "": return False
    return True

def genera_griglia_logica(R, C, parole_italiane):
    """Genera la matrice del cruciverba."""
    griglia = [["" for _ in range(C)] for _ in range(R)]
    
    pool_parole = random.sample(parole_italiane, min(1000, len(parole_italiane)))
    parole_piazzate = []

    # 1. Piazza la prima parola al centro
    prima_parola = pool_parole.pop(0)
    while len(prima_parola) > C - 2 and pool_parole:
        prima_parola = pool_parole.pop(0)
    
    r_inizio = R // 2
    c_inizio = (C - len(prima_parola)) // 2
    
    for i, char in enumerate(prima_parola):
        griglia[r_inizio][c_inizio + i] = char
    parole_piazzate.append({"parola": prima_parola, "direzione": "H", "riga": r_inizio, "col": c_inizio})

    # 2. Inserimento a incrocio
    tentativi = 0
    while pool_parole and tentativi < 500:
        parola = pool_parole.pop(0)
        piazzata = False
        
        for p_info in parole_piazzate:
            if piazzata: break
            for i, p_char in enumerate(parola):
                if piazzata: break
                for j, info_char in enumerate(p_info["parola"]):
                    if p_char == info_char:
                        if p_info["direzione"] == "H":
                            nuova_dir = "V"
                            nuova_riga = p_info["riga"] - i
                            nuova_col = p_info["col"] + j
                        else:
                            nuova_dir = "H"
                            nuova_riga = p_info["riga"] + j
                            nuova_col = p_info["col"] - i
                        
                        if 0 <= nuova_riga < R and 0 <= nuova_col < C:
                            if controlla_spazio(griglia, parola, nuova_riga, nuova_col, nuova_dir, R, C):
                                for k, c in enumerate(parola):
                                    if nuova_dir == "H":
                                        griglia[nuova_riga][nuova_col + k] = c
                                    else:
                                        griglia[nuova_riga + k][nuova_col] = c
                                parole_piazzate.append({"parola": parola, "direzione": nuova_dir, "riga": nuova_riga, "col": nuova_col})
                                piazzata = True
                                break
        tentativi += 1
    return griglia

def disegna_griglia_html(griglia, R, C):
    """Crea una tabella HTML per renderizzare il cruciverba in modo stiloso."""
    html = '<table style="border-collapse: collapse; margin-left: auto; margin-right: auto; background-color: black;">'
    for r in range(R):
        html += '<tr>'
        for c in range(C):
            lettera = griglia[r][c]
            if lettera:
                html += f'<td style="width: 30px; height: 30px; background-color: white; color: black; text-align: center; font-weight: bold; font-family: monospace; border: 1px solid #333;">{lettera}</td>'
            else:
                html += f'<td style="width: 30px; height: 30px; background-color: black; border: 1px solid #333;"></td>'
        html += '</tr>'
    html += '</table>'
    return html

# --- Interfaccia Streamlit ---
st.title("🧩 Generatore Cruciverba")
st.markdown("Crea uno schema a incroci liberi direttamente dal tuo iPad.")

parole_italiane = carica_dizionario()

col1, col2 = st.columns(2)
with col1:
    righe = st.number_input("Numero di Righe", min_value=5, max_value=30, value=15, step=1)
with col2:
    colonne = st.number_input("Numero di Colonne", min_value=5, max_value=30, value=15, step=1)

if st.button("Genera Cruciverba", type="primary", use_container_width=True):
    with st.spinner("Creazione degli incroci in corso..."):
        griglia = genera_griglia_logica(righe, colonne, parole_italiane)
        html_griglia = disegna_griglia_html(griglia, righe, colonne)
        
        st.markdown("---")
        # Mostriamo l'HTML renderizzato
        st.markdown(html_griglia, unsafe_allow_html=True)
        st.markdown("---")
        st.success("Cruciverba generato con successo!")
