import streamlit as st
import random
import urllib.request

# --- Configurazioni della pagina ---
st.set_page_config(page_title="Generatore Cruciverba Professionale", layout="centered")

# URL di un dizionario italiano corposo e completo (oltre 60.000 lemmi)
DICT_URL = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/paroleitaliane/parole_italiane.txt"

@st.cache_data(show_spinner="Download del dizionario italiano completo in corso...")
def carica_dizionario_completo():
    """Scarica il dizionario completo dal web e lo indicizza."""
    try:
        response = urllib.request.urlopen(DICT_URL, timeout=10)
        words = response.read().decode('utf-8').splitlines()
        # Pulizia e filtraggio dei lemmi (solo lettere, lunghezza minima 2 caratteri)
        parole = [w.upper().strip() for w in words if w.isalpha() and len(w) >= 2]
    except Exception as e:
        # Fallback di emergenza se la connessione fallisce
        parole = ["ENIGMA", "PYTHON", "STREAMLIT", "GITHUB", "IPAD", "INFORMATICA", 
                  "CRUSCA", "TRECCANI", "PAROLA", "LOGICA", "CRUCIBA", "GRIGLIA"]
    
    # Ordiniamo dal lemma più lungo a quello più corto per ottimizzare l'incastro iniziale
    parole.sort(key=len, reverse=True)
    return parole

def controlla_vincoli_spazio(griglia, parola, riga, col, direzione, R, C):
    """
    Verifica se la parola può essere inserita garantendo che ci sia
    una casella nera (o il bordo della griglia) all'inizio e alla fine.
    """
    lunghezza = len(parola)
    
    if direzione == "H":
        # Controllo sconfinamento bordi
        if col + lunghezza > C: return False
        
        # Vincolo casella nera all'INIZIO (se non è sul bordo sinistro)
        if col > 0 and griglia[riga][col-1] != "◼": return False
        # Vincolo casella nera alla FINE (se non è sul bordo destro)
        if col + lunghezza < C and griglia[riga][col+lunghezza] != "◼" and griglia[riga][col+lunghezza] != "": return False
        
        # Controllo sovrapposizioni delle lettere e adiacenze laterali
        for i, char in enumerate(parola):
            c_corrente = col + i
            # Lettera diversa già presente? Collisione.
            if griglia[riga][c_corrente] != "" and griglia[riga][c_corrente] != "◼" and griglia[riga][c_corrente] != char:
                return False
            # Se la cella è una casella nera bloccata, non possiamo sovrascriverla con una lettera
            if griglia[riga][c_corrente] == "◼":
                return False
            
            # Se la cella è vuota, non deve toccare altre parole sopra o sotto (evita parole attaccate senza senso)
            if griglia[riga][c_corrente] == "":
                if riga > 0 and griglia[riga-1][c_corrente] != "" and griglia[riga-1][c_corrente] != "◼": return False
                if riga < R-1 and griglia[riga+1][c_corrente] != "" and griglia[riga+1][c_corrente] != "◼": return False
                
    else: # Direzione Verticale "V"
        # Controllo sconfinamento bordi
        if riga + lunghezza > R: return False
        
        # Vincolo casella nera all'INIZIO (se non è sul bordo superiore)
        if riga > 0 and griglia[riga-1][col] != "◼": return False
        # Vincolo casella nera alla FINE (se non è sul bordo inferiore)
        if riga + lunghezza < R and griglia[riga+lunghezza][col] != "◼" and griglia[riga+lunghezza][col] != "": return False
        
        # Controllo sovrapposizioni delle lettere e adiacenze laterali
        for i, char in enumerate(parola):
            r_corrente = riga + i
            if griglia[r_corrente][col] != "" and griglia[r_corrente][col] != "◼" and griglia[r_corrente][col] != char:
                return False
            if griglia[r_corrente][col] == "◼":
                return False
            
            if griglia[r_corrente][col] == "":
                if col > 0 and griglia[r_corrente][col-1] != "" and griglia[r_corrente][col-1] != "◼": return False
                if col < C-1 and griglia[r_corrente][col+1] != "" and griglia[r_corrente][col+1] != "◼": return False
                
    return True

def inserisci_parola_e_nere(griglia, parola, riga, col, direzione, R, C):
    """Piazza la parola nella griglia e posiziona le caselle nere ai suoi estremi."""
    lunghezza = len(parola)
    
    # Inserimento lettere
    for k, char in enumerate(parola):
        if direzione == "H":
            griglia[riga][col + k] = char
        else:
            griglia[riga + k][col] = char
            
    # Posizionamento caselle nere di delimitazione
    if direzione == "H":
        if col > 0: 
            griglia[riga][col-1] = "◼"
        if col + lunghezza < C: 
            griglia[riga][col+lunghezza] = "◼"
    else:
        if riga > 0: 
            griglia[riga-1][col] = "◼"
        if riga + lunghezza < R: 
            griglia[riga+lunghezza][col] = "◼"

def genera_struttura_cruciverba(R, C, dizionario):
    """Algoritmo principale di generazione ad incastri con vincoli rigidi sulle caselle nere."""
    griglia = [["" for _ in range(C)] for _ in range(R)]
    
    # Estraiamo un sottoinsieme casuale dal dizionario gigante per variare lo schema a ogni click
    pool_parole = random.sample(dizionario, min(2000, len(dizionario)))
    parole_inserite = []

    # 1. Posizionamento della prima parola al centro dello schema
    prima_parola = pool_parole.pop(0)
    while len(prima_parola) > C - 2 and pool_parole:
        prima_parola = pool_parole.pop(0)
    
    r_centro = R // 2
    c_centro = (C - len(prima_parola)) // 2
    
    inserisci_parola_e_nere(griglia, prima_parola, r_centro, c_centro, "H", R, C)
    parole_inserite.append({"parola": prima_parola, "direzione": "H", "riga": r_centro, "col": c_centro})

    # 2. Ciclo di incrocio per i lemmi successivi
    tentativi = 0
    while pool_parole and tentativi < 800:
        parola = pool_parole.pop(0)
        inserita = False
        
        # Prova a incrociare con una delle parole già presenti in griglia
        for p_info in parole_inserite:
            if inserita: break
            
            for i, carattere_nuovo in enumerate(parola):
                if inserita: break
                
                for j, carattere_esistente in enumerate(p_info["parola"]):
                    if carattere_nuovo == carattere_esistente:
                        # Calcola le coordinate di partenza per la nuova parola basandoti sull'incrocio
                        if p_info["direzione"] == "H":
                            nuova_dir = "V"
                            nuova_riga = p_info["riga"] - i
                            nuova_col = p_info["col"] + j
                        else:
                            nuova_dir = "H"
                            nuova_riga = p_info["riga"] + j
                            nuova_col = p_info["col"] - i
                        
                        # Verifica i limiti e i vincoli delle caselle nere
                        if 0 <= nuova_riga < R and 0 <= nuova_col < C:
                            if controlla_vincoli_spazio(griglia, parola, nuova_riga, nuova_col, nuova_dir, R, C):
                                inserisci_parola_e_nere(griglia, parola, nuova_riga, nuova_col, nuova_dir, R, C)
                                parole_inserite.append({
                                    "parola": parola, 
                                    "direzione": nueva_dir, 
                                    "riga": nuova_riga, 
                                    "col": nuova_col
                                })
                                inserita = True
                                break
        tentativi += 1
        
    # Riempie gli spazi vuoti rimanenti trasformandoli in caselle nere alla fine del processo
    for r in range(R):
        for c in range(C):
            if griglia[r][c] == "":
                griglia[r][c] = "◼"
                
    return griglia

def renderizza_cruciverba_html(griglia, R, C):
    """Genera la tabella HTML/CSS per visualizzare correttamente la griglia su iPad e mobile."""
    html = '<table style="border-collapse: collapse; margin: 20px auto; background-color: #000; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">'
    for r in range(R):
        html += '<tr>'
        for c in range(C):
            cella = griglia[r][c]
            if cella == "◼":
                # Casella Nera
                html += '<td style="width: 32px; height: 32px; background-color: #000; border: 1px solid #444;"></td>'
            else:
                # Casella Bianca con Lettera
                html += f'<td style="width: 32px; height: 32px; background-color: #fff; color: #000; text-align: center; font-weight: bold; font-family: \'Courier New\', Courier, monospace; font-size: 16px; border: 1px solid #000;">{cella}</td>'
        html += '</tr>'
    html += '</table>'
    return html

# --- Interfaccia Utente Streamlit ---
st.title("🧩 Generatore Cruciverba Professionale")
st.markdown("Genera schemi enigmistici con incroci verticali/orizzontali e delimitazione rigorosa delle caselle nere.")

# Carica il super dizionario
lista_lemmi = carica_dizionario_completo()
st.caption(f"Database pronto: **{len(lista_lemmi):,}** lemmi italiani caricati in memoria.")

# Input dimensioni
col1, col2 = st.columns(2)
with col1:
    righe = st.number_input("Righe griglia", min_value=8, max_value=25, value=12, step=1)
with col2:
    colonne = st.number_input("Colonne griglia", min_value=8, max_value=25, value=12, step=1)

if st.button("Genera Schema", type="primary", use_container_width=True):
    with st.spinner("Calcolo degli incroci e piazzamento caselle nere..."):
        mappa_cruciverba = genera_struttura_cruciverba(righe, colonne, lista_lemmi)
        codice_html = renderizza_cruciverba_html(mappa_cruciverba, righe, colonne)
        
        st.markdown("---")
        st.markdown(codice_html, unsafe_allow_html=True)
        st.markdown("---")
        st.success("Cruciverba generato correttamente!")
