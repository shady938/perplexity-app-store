import streamlit as st
import json
from openai import OpenAI

# 1. CONFIGURAZIONE DELLA PAGINA (Stile grafico moderno e minimalista)
st.set_page_config(
    page_title="App Store AI Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS per dare un look premium in stile Perplexity
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 900px; }
    h1 { font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; color: #1e3c72; text-align: center; }
    .subtitle { text-align: center; color: #7f8c8d; margin-bottom: 2rem; font-size: 1.1rem; }
    .stTextInput { margin-top: 1rem; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; border: none; padding: 0.5rem 2rem; border-radius: 5px;
    }
    .app-card { background-color: #f8f9fa; border: 1px solid #e1e2e6; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
    </style>
""", unsafe_allowed_html=True)

# 2. INIZIALIZZAZIONE CLIENT IA
# Inserisci qui la tua chiave o digitala nella barra laterale dell'app
API_KEY = st.sidebar.text_input("OpenAI API Key", type="password", value="")

# 3. DATABASE DELLE APP (Mock di ciò che verrebbe estratto dal Vector DB)
MOCK_VECTOR_DB = [
    {
        "id": "app_01",
        "nome": "CapCut",
        "categoria": "Video Editing",
        "prezzo": "Gratuito con acquisti in-app",
        "descrizione": "Editor video avanzato con strumenti IA integrati per la generazione automatica di sottotitoli, rimozione dello sfondo ed effetti di tendenza. Ottimizzato per formati verticali (TikTok, Reels).",
        "punteggio_utenti": "4.7/5",
        "privacy": "Raccoglie dati di utilizzo e identificativi."
    },
    {
        "id": "app_02",
        "nome": "LumaFusion",
        "categoria": "Video Editing Professional",
        "prezzo": "34.99€ (Pagamento singolo)",
        "descrizione": "Multi-traccia professionale per iOS/iPadOS. Supporta LUT personalizzate, color grading avanzato, e file video ad alto bitrate. Nessun abbonamento richiesto.",
        "punteggio_utenti": "4.8/5",
        "privacy": "Nessun dato tracciato o collegato all'utente."
    },
    {
        "id": "app_03",
        "nome": "DaVinci Resolve iPad",
        "categoria": "Video Editing Professional",
        "prezzo": "Freemium (Studio Upgrade a 94.99€)",
        "descrizione": "Trasposizione fedele del software desktop. Strumenti di correzione colore da oscar e montaggio non lineare avanzato. Ottimizzato esclusivamente per Apple Silicon M1/M2/M3.",
        "punteggio_utenti": "4.5/5",
        "privacy": "Dati gestiti localmente sul dispositivo."
    }
]

# 4. FUNZIONE CORE DI ANALISI IA
def esegui_ricerca_app_store(query_utente, api_key):
    client = OpenAI(api_key=api_key)
    
    system_prompt = (
        "Sei l'assistente virtuale avanzato dell'App Store AI. Il tuo obiettivo è analizzare la richiesta "
        "dell'utente, valutare le applicazioni fornite nel contesto ed estrarre un report di confronto chiaro.\n\n"
        "Struttura la tua risposta tassativamente con le seguenti sezioni:\n"
        "1. **Sintesi dell'Analisi**: Risposta diretta ed estrazione dei requisiti dell'utente.\n"
        "2. **Tabella di Confronto**: Tabella Markdown con colonne [Applicazione | Prezzo | Caratteristica Chiave | Valutazione].\n"
        "3. **Analisi Verticale dei Candidati**: Breve focus su Pro e Contro delle singole applicazioni rispetto alla query.\n"
        "4. **Il Verdetto dell'AI**: Raccomandazione finale personalizzata."
    )
    
    user_prompt = f"CONTESTO APPLICAZIONI:\n{json.dumps(MOCK_VECTOR_DB, indent=2)}\n\nQUERY UTENTE:\n\"{query_utente}\""
    
    # Usiamo lo streaming per visualizzare la risposta in tempo reale (UX stile Perplexity)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        stream=True
    )
    return stream

# 5. INTERFACCIA UTENTE (UI)
st.markdown("<h1>🔍 App Store AI Search Engine</h1>", unsafe_allowed_html=True)
st.markdown("<p class='subtitle'>Trova l'applicazione perfetta spiegando le tue esigenze, non le parole chiave.</p>", unsafe_allowed_html=True)

# Visualizzazione delle fonti disponibili (Simulando la UI di Perplexity che mostra le fonti in alto)
with st.expander("🌐 Fonti Database analizzate in tempo reale", expanded=False):
    cols = st.columns(len(MOCK_VECTOR_DB))
    for idx, app in enumerate(MOCK_VECTOR_DB):
        with cols[idx]:
            st.markdown(f"**📱 {app['nome']}**\n*{app['categoria']}*\nValutazione: {app['punteggio_utenti']}")

# Barra di ricerca principale
query = st.text_input(
    label="Cosa stai cercando?", 
    placeholder="Es: Voglio un'app per montare video su iPad, non voglio abbonamenti e cerco qualcosa di rapido con IA...",
    label_visibility="collapsed"
)

# Bottone di invio e gestione della richiesta
if st.button("Chiedi all'IA") or query:
    if not API_KEY:
        st.warning("⚠️ Per favore, inserisci la tua OpenAI API Key nella barra laterale sinistra per avviare la ricerca.")
    elif not query.strip():
        st.info("💡 Scrivi qualcosa nella barra di ricerca prima di inviare!")
    else:
        st.subheader("🤖 Risposta dell'Assistente IA")
        
        # Effetto di caricamento iniziale
        with st.spinner("Analizzando il database delle applicazioni..."):
            try:
                # Esecuzione e streaming della risposta a schermo
                risposta_stream = esegui_ricerca_app_store(query, API_KEY)
                
                # Contenitore dinamico per il testo in streaming
                placeholder = st.empty()
                testo_completo = ""
                
                for chunk in risposta_stream:
                    if chunk.choices[0].delta.content:
                        testo_completo += chunk.choices[0].delta.content
                        placeholder.markdown(testo_completo)
                        
            except Exception as e:
                st.error(f"Si è verificato un errore durante la comunicazione con l'IA: {e}")
