import streamlit as st
import random

st.set_page_config(page_title="Generatore di Cruciverba", layout="centered")

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
# (Incolla qui le funzioni controlla_vincoli_spazio, inserisci_parola_e_nere, genera_griglia, ecc.)


# --- UI MODIFICATA PER GRIGLIE PIÙ AMPIE ---
st.title("🧩 Generatore Cruciverba XXL")

lista_lemmi = prepara_dizionario()
st.sidebar.info(f"Lemmi pronti: {len(lista_lemmi)}")

righe = st.sidebar.slider("Righe", 9, 13, 12)
colonne = st.sidebar.slider("Colonne", 9, 22, 22)

if st.button("Genera Schema Denso"):
    with st.spinner("Calcolo incroci..."):
        mappa = genera_struttura_cruciverba(righe, colonne, lista_lemmi)
        st.markdown(renderizza_cruciverba_html(mappa, righe, colonne), unsafe_allow_html=True)
