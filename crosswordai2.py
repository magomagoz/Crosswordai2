import tkinter as tk
from tkinter import messagebox
import random
import urllib.request
import threading

DICT_URL = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/paroleitaliane/parole_italiane.txt"
parole_italiane = []

def scarica_dizionario():
    """Scarica il dizionario in background."""
    global parole_italiane
    try:
        response = urllib.request.urlopen(DICT_URL, timeout=5)
        words = response.read().decode('utf-8').splitlines()
        parole_italiane = [w.upper() for w in words if w.isalpha() and len(w) > 2]
    except Exception:
        parole_italiane = ["ENIGMA", "PYTHON", "TRECCANI", "CRUSCA", "COMPUTER", "INFORMATICA", 
                           "GATTO", "CANE", "SOLE", "LUNA", "MARE", "VITA", "PROGRAMMAZIONE"]
    
    # Ordina per lunghezza decrescente, aiuta ad avere incroci migliori se usiamo le parole lunghe per prime
    parole_italiane.sort(key=len, reverse=True)
    btn_genera.config(text="Genera Cruciverba", state=tk.NORMAL)

def controlla_spazio(griglia, parola, riga, col, direzione, R, C):
    """Verifica se la parola può essere posizionata senza collisioni non valide."""
    if direzione == "H":
        if col + len(parola) > C: return False
        # Evita attaccamenti all'inizio e alla fine
        if col > 0 and griglia[riga][col-1] != "": return False
        if col + len(parola) < C and griglia[riga][col+len(parola)] != "": return False
        
        for i, char in enumerate(parola):
            c_corrente = col + i
            # Se la cella è occupata da una lettera diversa, è un conflitto
            if griglia[riga][c_corrente] != "" and griglia[riga][c_corrente] != char:
                return False
            # Se la cella è vuota, assicurati che non tocchi altre lettere sopra o sotto
            if griglia[riga][c_corrente] == "":
                if riga > 0 and griglia[riga-1][c_corrente] != "": return False
                if riga < R-1 and griglia[riga+1][c_corrente] != "": return False
    else: # Verticale ("V")
        if riga + len(parola) > R: return False
        # Evita attaccamenti all'inizio e alla fine
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

def genera_cruciverba():
    """Genera la griglia a incroci."""
    try:
        R = int(entry_righe.get())
        C = int(entry_colonne.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci numeri interi validi per righe e colonne.")
        return

    for widget in frame_griglia.winfo_children():
        widget.destroy()

    if not parole_italiane:
        messagebox.showwarning("Attesa", "Dizionario in caricamento, attendi.")
        return

    # Inizializza la griglia vuota
    griglia = [["" for _ in range(C)] for _ in range(R)]
    
    # Seleziona un pool di parole casuali dal dizionario (mescoliamo un sottoinsieme per varietà)
    pool_parole = random.sample(parole_italiane, min(1000, len(parole_italiane)))
    parole_piazzate = []

    # 1. Piazza la prima parola al centro (orizzontale)
    prima_parola = pool_parole.pop(0)
    while len(prima_parola) > C - 2 and pool_parole:
        prima_parola = pool_parole.pop(0)
    
    r_inizio = R // 2
    c_inizio = (C - len(prima_parola)) // 2
    
    # Inserimento della prima parola
    for i, char in enumerate(prima_parola):
        griglia[r_inizio][c_inizio + i] = char
    parole_piazzate.append({"parola": prima_parola, "direzione": "H", "riga": r_inizio, "col": c_inizio})

    # 2. Tenta di incrociare le altre parole
    tentativi = 0
    while pool_parole and tentativi < 500: # Limite per non bloccare il programma
        parola = pool_parole.pop(0)
        piazzata = False
        
        # Cerca un incrocio con le parole già piazzate
        for p_info in parole_piazzate:
            if piazzata: break
            
            # Cerca lettere in comune
            for i, p_char in enumerate(parola):
                if piazzata: break
                
                for j, info_char in enumerate(p_info["parola"]):
                    if p_char == info_char:
                        # Trovato un punto di incrocio potenziale
                        if p_info["direzione"] == "H":
                            nuova_dir = "V"
                            nuova_riga = p_info["riga"] - i
                            nuova_col = p_info["col"] + j
                        else:
                            nuova_dir = "H"
                            nuova_riga = p_info["riga"] + j
                            nuova_col = p_info["col"] - i
                        
                        # Controlla se le coordinate base sono dentro la griglia
                        if 0 <= nuova_riga < R and 0 <= nuova_col < C:
                            if controlla_spazio(griglia, parola, nuova_riga, nuova_col, nuova_dir, R, C):
                                # Piazza la parola
                                for k, c in enumerate(parola):
                                    if nuova_dir == "H":
                                        griglia[nuova_riga][nuova_col + k] = c
                                    else:
                                        griglia[nuova_riga + k][nuova_col] = c
                                parole_piazzate.append({"parola": parola, "direzione": nuova_dir, "riga": nuova_riga, "col": nuova_col})
                                piazzata = True
                                break
        tentativi += 1

    # 3. Disegna la griglia su Tkinter
    for r in range(R):
        for c in range(C):
            lettera = griglia[r][c]
            bg_color = "white" if lettera else "black"
            tk.Label(frame_griglia, text=lettera, bg=bg_color, fg="black",
                     width=2, height=1, font=("Courier", 16, "bold"), relief="solid", borderwidth=1).grid(row=r, column=c, padx=1, pady=1)

# --- Setup Interfaccia ---
root = tk.Tk()
root.title("Generatore Cruciverba a Incroci")
root.geometry("800x800")

frame_controlli = tk.Frame(root)
frame_controlli.pack(pady=20)

tk.Label(frame_controlli, text="Righe:").grid(row=0, column=0, padx=5)
entry_righe = tk.Entry(frame_controlli, width=5)
entry_righe.grid(row=0, column=1, padx=5)
entry_righe.insert(0, "15") 

tk.Label(frame_controlli, text="Colonne:").grid(row=0, column=2, padx=5)
entry_colonne = tk.Entry(frame_controlli, width=5)
entry_colonne.grid(row=0, column=3, padx=5)
entry_colonne.insert(0, "15") 

btn_genera = tk.Button(frame_controlli, text="Caricamento Dizionario...", command=genera_cruciverba, state=tk.DISABLED)
btn_genera.grid(row=0, column=4, padx=20)

frame_griglia = tk.Frame(root, bg="gray")
frame_griglia.pack(padx=10, pady=10)

threading.Thread(target=scarica_dizionario, daemon=True).start()

root.mainloop()
