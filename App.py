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

# 5. API Ključ za Gemini
st.sidebar.markdown("---")
api_key_input = st.sidebar.text_input("Unesite Google Gemini API ključ:", type="password")

# Inicijalizacija Gemini klijenta
client = None
if api_key_input:
    try:
        client = genai.Client(api_key_=api_key_input)
    except Exception as e:
        st.sidebar.error(f"Greška pri inicijalizaciji: {e}")
else:
    st.sidebar.warning("Molimo unesite Google Gemini API ključ da bi bot radio.")

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
    - Uvek koristi proverene izvore sa domaćih i stranih sajtova (putem pretrage ako je potrebno).
    - Kada računaš nutritivnu vrednost, navedi okvirne kalorije i makronutriente (proteini, ugljeni hidrati, masti).
    """

# --- TAB 1: RECEPTI I NUTRITIVNE VREDNOSTI ---
with tab1:
    st.header("Pretraga recepata i nutritivnih vrednosti")
    recipe_query = st.text_input("Šta biste želeli da spremite ili saznate?", placeholder="npr. Brzi veganski ručak sa tofuom i povrćem")
    
    if st.button("Pronađi recept i nutritivne vrednosti", key="btn_recipe"):
        if not client:
            st.error("Unesite Gemini API ključ u levom meniju!")
        elif not recipe_query:
            st.warning("Unesite naziv jela ili sastojak.")
        else:
            with st.spinner("Pretražujem recepte i računam nutritivne vrednosti..."):
                try:
                    prompt = f"""
                    Korisnik traži: {recipe_query}.
                    Ponašaj se u skladu sa sledećim pravilima:
                    {get_system_instruction()}
                    
                    Daj mi:
                    1. Detaljan recept prilagođen pravilima ishrane.
                    2. Tačne ili okvirne nutritivne vrednosti (kalorije, proteini, ugljeni hidrati, masti).
                    3. Koristi podatke sa pouzdanih kulinarskih sajtova (domaćih i stranih).
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Došlo je do greške: {e}")

# --- TAB 2: ŠTA DA SKUVAM OD OVE TRI NAMIRNICE ---
with tab2:
    st.header("Kulinarski asistent iz frižidera")
    st.write("Unesite namirnice koje trenutno imate (npr. 3 ili više sastojaka), a bot će smisliti recept, reći šta vam fali i uklopiti se u vaš režim.")
    
    available_ingredients = st.text_input("Namirnice koje imam u frižideru:", placeholder="npr. tofu, spanać, pirinač, šargarepa")
    
    if st.button("Smisli jelo i proveri šta fali", key="btn_fridge"):
        if not client:
            st.error("Unesite Gemini API ključ u levom meniju!")
        elif not available_ingredients:
            st.warning("Unesite namirnice koje imate.")
        else:
            with st.spinner("Analiziram sastojke i pravim kombinaciju..."):
                try:
                    prompt = f"""
                    Imam sledeće namirnice u frižideru: {available_ingredients}.
                    Poštujući sledeća pravila:
                    {get_system_instruction()}
                    
                    1. Predloži odličan recept koji koristi ove namirnice (ili većinu njih).
                    2. Jasno naglasi **šta mi fali** od dodatnih sastojaka da bih spremio ovo jelo.
                    3. Izračunaj nutritivne vrednosti za kompletno jelo.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Došlo je do greške: {e}")

# --- TAB 3: GDE DA KUPIM U BLIZINI ---
with tab3:
    st.header("Pretraga prodavnica u radijusu")
    item_to_buy = st.text_input("Šta tražite da kupite?", placeholder="npr. dimljeni tofu, nutritivni kvasac, tempeh")
    
    if st.button("Pronađi gde ima da se kupi", key="btn_shop"):
        if not client:
            st.error("Unesite Gemini API ključ u levom meniju!")
        elif not item_to_buy:
            st.warning("Unesite naziv namirnice koju tražite.")
        else:
            with st.spinner(f"Pretražujem prodavnice zdrave hrane i markete u krugu od {search_radius} km od lokacije {user_location}..."):
                try:
                    prompt = f"""
                    Korisnik traži namirnicu: {item_to_buy}.
                    Lokacija korisnika: {user_location}.
                    Maksimalni radijus pretrage: {search_radius} km.
                    
                    Pretraži internet i pronađi konkretne prodavnice zdrave hrane, supermarkete ili specijalizovane radnje blizu ove lokacije u tom radijusu gde se ova namirnica može kupiti. Navedi nazive prodavnica, okvirne lokacije/adrese ako su dostupne na mapi ili netu, i savetuj korisnika gde da ide.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Došlo je do greške: {e}")
