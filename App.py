import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Food & Nutrition Bot",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Moj Lični AI Food & Nutrition Agent")
st.write("Pametni pomoćnik za ishranu, recepte, nutritivne vrednosti i kupovinu u blizini.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Podešavanja profila")

diet_mode = st.sidebar.selectbox(
    "Režim ishrane:",
    ["Veganski i Vegetarijanski (Obe opcije)", "Isključivo Veganski", "Isključivo Vegetarijanski"]
)

excluded_items = st.sidebar.text_area(
    "Namirnice koje STROGO izbacujem:",
    value="ovsena kaša"
)

preferred_items = st.sidebar.text_area(
    "Preferirane namirnice:",
    value="tofu, tempeh, kinoaa, proso, leblebije"
)

st.sidebar.markdown("---")
user_location = st.sidebar.text_input("Vaša lokacija:", value="Blok 45, Novi Beograd")
search_radius = st.sidebar.slider("Radijus pretrage (km):", min_value=1, max_value=20, value=5)

# Učitavanje API ključa iz Streamlit Secrets-a
api_key_input = st.secrets.get("GEMINI_API_KEY", "")

client = None
if api_key_input:
    try:
        client = genai.Client(api_key=api_key_input)
    except Exception as e:
        st.sidebar.error(f"Greška: {e}")
else:
    st.sidebar.error("API ključ nije pronađen u Secrets podešavanjima!")

# --- TABOVI ---
tab1, tab2, tab3 = st.tabs([
    "🍳 Recepti", 
    "🧊 Iz frižidera", 
    "🛒 Kupovina"
])

def get_instructions():
    return f"Režim: {diet_mode}. Izbaci: {excluded_items}. Voli: {preferred_items}."

with tab1:
    st.header("Pretraga recepata")
    query = st.text_input("Šta želiš da spremiš?", placeholder="npr. Veganski gulaš")
    
    if st.button("Pronađi recept", key="b1"):
        if not client:
            st.error("Nema API ključa!")
        elif not query:
            st.warning("Unesi naziv jela.")
        else:
            with st.spinner("Pretražujem..."):
                try:
                    p = f"Nađi recept za: {query}. Pravila: {get_instructions()}. Daj sastojke, pripremu i kalorije."
                    res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=p,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Greška: {e}")

with tab2:
    st.header("Šta da skuvam iz frižidera")
    ing = st.text_input("Namirnice koje imaš:", placeholder="npr. tofu, spanać, pirinač")
    
    if st.button("Smisli jelo", key="b2"):
        if not client:
            st.error("Nema API ključa!")
        elif not ing:
            st.warning("Unesi namirnice.")
        else:
            with st.spinner("Analiziram..."):
                try:
                    p = f"Imam u frižideru: {ing}. Pravila: {get_instructions()}. Predloži recept, šta fali od namirnica i nutritivne vrednosti."
                    res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=p,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Greška: {e}")

with tab3:
    st.header("Gde kupiti u blizini")
    item = st.text_input("Šta tražiš da kupiš?", placeholder="npr. tempeh")
    
    if st.button("Pronađi prodavnice", key="b3"):
        if not client:
            st.error("Nema API ključa!")
        elif not item:
            st.warning("Unesi namirnicu.")
        else:
            with st.spinner("Pretražujem prodavnice..."):
                try:
                    p = f"Gde se može kupiti '{item}' blizu lokacije {user_location} u radijusu od {search_radius} km? Pronađi konkretne prodavnice."
                    res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=p,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Greška: {e}")
