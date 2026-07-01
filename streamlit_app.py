import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.graph_objects as go

# Name der Datei, in der wir die Daten lokal speichern wollen
DATEN_DATEI = "athleten_daten.csv"

# --- SEITEN-KONFIGURATION (Tab-Titel im Browser) ---
st.set_page_config(page_title="Performance Tracker", page_icon="🏆", layout="wide")

# --- ROLLEN-AUSWAHL IN DER SIDEBAR ---
st.sidebar.markdown("### 🔐 Loginbereich")
rolle = st.sidebar.radio("Deine Rolle auswählen:", ["🏃‍♂️ Athlet", "📊 Trainer"])
st.sidebar.markdown("---")


# --- ANSICHT 1: ATHLETEN-ANSICHT (Eingabeformular) ---
if rolle == "🏃‍♂️ Athlet":
    st.title("🏆 Athleten-Check-In")
    st.markdown("Bitte nimm dir **30 Sekunden** Zeit, um deinen aktuellen Zustand einzutragen. Deine Daten helfen, das Training optimal zu steuern.")
    
    # Eingabe-Bereich in einer schönen Box (Container)
    with st.container(border=True):
        name = st.text_input("Dein Name / Kürzel", placeholder="z.B. MJ23")
        
        col_date, col_sleep = st.columns(2)
        with col_date:
            # Das aktuelle Datum ist Standard, die Zukunft ist gesperrt, die Vergangenheit ist offen
            datum = st.date_input(
                "Datum", 
                value=date.today(),      # Standardwert ist HEUTE
                max_value=date.today()   # Später als HEUTE kann nicht ausgewählt werden
            )
        with col_sleep:
            schlaf = st.slider("Wie viele Stunden hast du geschlafen?", 0.0, 12.0, 8.0, step=0.5)

        stimmung = st.select_slider(
            "Wie ist deine aktuelle Stimmung?",
            options=["Sehr niedrig", "Eher niedrig", "Neutral", "Gut", "Voller Energie"],
            value="Neutral"
        )

        # Checkboxen nebeneinander platzieren für besseres Mobile-Layout
        st.markdown("**Zusätzliche Faktoren:**")
        col_mk, col_stress = st.columns(2)
        with col_mk:
            muskelkater = st.checkbox("Ich habe Muskelkater 🩹")
        with col_stress:
            stress = st.checkbox("Ich habe aktuell viel Stress 🤯")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Button zum Absenden
        if st.button("🚀 Check-In absenden", use_container_width=True):
            if name:
                neue_zeile = pd.DataFrame({
                    "Datum": [str(datum)],
                    "Name": [name.upper().strip()],
                    "Schlaf_Stunden": [schlaf],
                    "Stimmung": [stimmung],
                    "Muskelkater": [muskelkater],
                    "Stress": [stress]
                })
                
                if not os.path.isfile(DATEN_DATEI):
                    neue_zeile.to_csv(DATEN_DATEI, index=False, sep=";")
                else:
                    neue_zeile.to_csv(DATEN_DATEI, mode='a', header=False, index=False, sep=";")
                    
                st.success(f"Sehr gut, {name.upper()}! Deine Daten wurden erfolgreich übermittelt.")
                st.balloons()
            else:
                st.error("Bitte gib zuerst dein Kürzel/Namen ein, damit wir die Daten zuordnen können.")

# --- ANSICHT 2: TRAINER-ANSICHT (Dashboard mit Passwortschutz) ---
elif rolle == "📊 Trainer":
    st.title("📊 Trainer-Dashboard")
    st.markdown("Hier siehst du den aktuellen Zustand deines Teams sowie die Verläufe der letzten Tage.")
    
    # Passwortabfrage in der Seitenleiste
    passwort = st.sidebar.text_input("Trainer-Passwort:", type="password", placeholder="Passwort eingeben")
    
    if passwort == "trainer123":
        st.sidebar.success("Zugriff gewährt")
        
        if os.path.isfile(DATEN_DATEI):
            df = pd.read_csv(DATEN_DATEI, sep=";")
            alle_athleten = df["Name"].unique()
            stimmungs_mapping = {"Sehr niedrig": 1, "Eher niedrig": 2, "Neutral": 3, "Gut": 4, "Voller Energie": 5}
            
            # Für jeden Athleten eine eigene visuelle Karte erstellen
            for athlet in alle_athleten:
                with st.container(border=True): # Erzeugt einen schönen Rahmen um den Athleten
                    athleten_daten = df[df["Name"] == athlet].copy()
                    athleten_daten["Stimmung_Wert"] = athleten_daten["Stimmung"].map(stimmungs_mapping)
                    aktuell = athleten_daten.iloc[-1]
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"## 🏃‍♂️ {athlet}")
                        st.metric(label="Letzter Schlaf", value=f"{aktuell['Schlaf_Stunden']} h")
                        
                        # Warnsignale optisch hervorheben
                        mk_status = "🔴 Ja (Achtung)" if aktuell["Muskelkater"] else "🟢 Nein"
                        stress_status = "⚠️ Viel (Mentaler Fokus!)" if aktuell["Stress"] else "🟢 Normal"
                        
                        st.markdown(f"**Muskelkater:** {mk_status}")
                        st.markdown(f"**Stresslevel:** {stress_status}")
                        
                    with col2:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=athleten_daten["Datum"], y=athleten_daten["Schlaf_Stunden"], name="Schlaf (h)", mode="lines+markers", line=dict(color="#1f77
