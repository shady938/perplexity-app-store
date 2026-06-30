import streamlit as st
import json
from openai import OpenAI

# 1. CONFIGURAZIONE DELLA PAGINA
st.set_page_config(
    page_title="App Store AI Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Gestione dello stato della sessione (tiene il conto delle domande dell'utente)
if "contatore_domande" not in st.session_state:
    st.session_state.contatore_domande = 0

# LIMITE MASSIMO DI DOMANDE PER UTENTI GRATUITI
LIMITE_GRATIS = 5

# 2. INIZIALIZZAZIONE CLIENT IA
API_KEY = st.sidebar.text_input("OpenAI API Key", type="password", value="")

# 3. DATABASE DELLE APP (Mock)
MOCK_VECTOR_DB = [
    {"id": "app_01", "nome": "CapCut", "categoria": "Video Editing", "prezzo": "Gratuito con acquisti in-app", "descrizione": "Editor video avanzato con strumenti IA integrati per sottotitoli automatici.", "punteggio_utenti": "4.7/5"},
    {"id": "app_02", "nome": "LumaFusion", "categoria": "Video Editing Professional", "prezzo": "34.99€ (Pagamento singolo)", "descrizione": "Multi-traccia professionale per iOS/iPadOS senza abbonamento.", "punteggio_utenti": "4.8/5"},
    {"id": "app_03", "nome": "DaVinci Resolve iPad", "categoria": "Video Editing Professional", "prezzo": "Freemium", "descrizione": "Trasposizione del software desktop. Strumenti di correzione colore da oscar.", "punteggio_utenti": "4.5/5"}
]

def esegui_ricerca_app_store(query_utente, api_key):
    client = OpenAI(api_key=api_key)
    system_prompt = "Sei l'assistente dell'App Store AI. Fai un confronto e rispondi in Markdown con tabelle, pro e contro."
    user_prompt = f"CONTESTO:\n{json.dumps(MOCK_VECTOR_DB, indent=2)}\n\nQUERY:\n\"{query_utente}\""
    
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.2, stream=True
    )
    return stream

# 4. INTERFACCIA UTENTE (UI)
st.title("🔍 App Store AI Search Engine")
st.caption("Trova l'applicazione perfetta spiegando le tue esigenze.")

# Mostra all'utente quante ricerche gli rimangono
ricerche_rimaste = LIMITE_GRATIS - st.session_state.contatore_domande

if ricerche_rimaste > 0:
    st.write(f"💡 Hai a disposizione **{ricerche_rimaste}** ricerche gratuite per oggi.")
    
    # Barra di ricerca attiva
    query = st.text_input(label="Cosa stai cercando?", placeholder="Es: Voglio un'app per montare video...", label_visibility="collapsed")
    
    if st.button("Chiedi all'IA") and query:
        if not API_KEY:
            st.warning("⚠️ Inserisci la tua OpenAI API Key nella barra laterale a sinistra.")
        else:
            st.subheader("🤖 Risposta dell'Assistente IA")
            with st.spinner("Analizzando il database..."):
                try:
                    risposta_stream = esegui_ricerca_app_store(query, API_KEY)
                    placeholder = st.empty()
                    testo_completo = ""
                    for chunk in risposta_stream:
                        if chunk.choices[0].delta.content:
                            testo_completo += chunk.choices[0].delta.content
                            placeholder.markdown(testo_completo)
                    
                    # Aggiorna il contatore solo dopo una ricerca andata a buon fine
                    st.session_state.contatore_domande += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
else:
    # PAYWALL: Il contatore ha raggiunto il limite, blocca l'app e mostra l'offerta
    st.error("⚠️ Hai esaurito le tue 5 ricerche gratuite per oggi!")
    
    st.subheader("👑 Passa a Premium")
    st.write("Non interrompere le tue ricerche. Sblocca query IA illimitate, analisi avanzate della privacy e confronti dettagliati.")
    
    # Visualizzazione delle opzioni di prezzo affiancate
    col1, col2 = st.columns(2)
    with col1:
        st.info("### Piano Mensile\n**4,99 €** / mese\n\nDisdici quando vuoi")
        if st.button("Abbonati Mensile", key="btn_mensile"):
            st.success("💰 Reindirizzamento al pagamento (Stripe) in corso...")
            
    with col2:
        st.success("### Piano Annuale\n**40,00 €** / anno\n\nRisparmi il 33%!")
        if st.button("Abbonati Annuale", key="btn_annuale"):
            st.success("💰 Reindirizzamento al pagamento (Stripe) in corso...")

# Bottone di reset per permetterti di testare l'app durante lo sviluppo
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Contatore (Solo per Test)"):
    st.session_state.contatore_domande = 0
    st.rerun()
