import streamlit as st
import os
from google import genai
from google.genai import types

# Podešavanje stranice
st.set_page_config(
    page_title="AI Food & Nutrition Bot",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Moj Lični AI Food & Nutrition Agent")
st.write("Pametni pomoćnik za ishranu, recepte, nutritivne vrednosti i kupovinu u blizini.")

# --- SIDEBAR: KONFIGURACIJA PROFILA ---
st.sidebar.header("⚙️ Podešavanja profila")

# 1. Režim ishrane
diet_mode = st.sidebar.selectbox(
    "Režim ishrane:",
    ["Veganski i Vegetarijanski (Obe opcije)", "Isključivo Veganski", "Isključivo Vegetarijanski"]
)

# 2. Izbačene namirnice
excluded_items = st.sidebar.text_area(
    "Namirnice koje STROGO izbacujem:",
    value="ovsena kaša",
    help="Unesite namirnice koje ne želite da se pojavljuju u receptima (odvojite zarezom)."
)

# 3. Preferirane namirnice
preferred_items = st.sidebar.text_area(
    "Preferirane namirnice (opciono):",
    value="tofu, tempeh, kinoaa, proso, leblebije, zamrznute borovnice",
    help="Namirnice koje volite i želite češće u receptima."
)

st.sidebar.markdown("---")
st.sidebar.header("📍 Lokacija i Pretraga")

# 4. Lokacija i radijus
user_location = st.sidebar.text_input("Vaša lokacija:", value="Blok 45, Novi Beograd")
search_radius = st.sidebar.slider("Radijus pretrage (km):", min_value=1, max_value=20, value=5)

# 5. Automatsko učitavanje Gemini API ključa iz Secrets-a
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

client = None
if api_key_input:
    try:
        client = genai.Client(api_key=api_key_input)
    except Exception as e:
        st.sidebar.error(f"Greška pri inicijalizaciji: {e}")
else:
    st.sidebar.error("API ključ nije pronađen u podešavanjima (Secrets). Unesite ga u Streamlit Settings.")

# --- GLAVNI DEO: TABOVI ---
tab1, tab2, tab3 = st.tabs([
    "🍳 Recepti i Nutritivne Vrednosti", 
    "🧊 Šta da skuvam (Iz frižidera)", 
    "🛒 Gde da kupim u blizini"
])

# Funkcija za generisanje system prompt-a na osnovu podešavanja
def get_system_instruction():
    return f"""
    Ti si stručni AI nutricionista i kuvar. Tvoja pravila su stroga i moraju se poštovati:
    - Izabrani režim ishrane: {diet_mode}.
    - Namirnice koje se STROGO ISJUČUJU i nikada se ne smeju naći u receptima: {excluded_items}.
    - Preferirane namirnice koje treba češće koristiti ako je moguće: {preferred_items}.
    - Uvek koristi proverene izvore sa domaćih i stranih sajtova (putem
