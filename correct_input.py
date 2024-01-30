import streamlit as st

def correct_input(input_string):
    
    titles = {
          "nights_are_cold_sometimes" : r"secret/nights_are_cold_sometimes.mp3",
          "a_long_way_home" : r"secret/a_long_way_home.mp3",
          "dumdomdamdemdim" : r"secret/dumdomdamdemdim.mp3",
          "funk-enmariechen" : r"secret/funk-enmariechen.mp3",
          "nochmal neuu22" : r"secret/nochmal neuu22.mp3",
          "quicksand_beach" : r"secret/quicksand_beach.mp3"
    }

    if "player" not in st.session_state:
          st.session_state["player"] = False
    if "reload" not in st.session_state:
          st.session_state["reload"] = None

    if input_string == "oelimar" or st.session_state["player"] == True:
            st.session_state["reload"] = True
            st.subheader("META_INF")
            st.session_state["player"] = True
            st.session_state["logo"] = r"secret/logo.png"
            selection = st.selectbox("Titel wählen", options=titles)
            audio_file = open(titles[selection], "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/ogg", start_time=0)
            return True

    if input_string == "Susimaus":
          customAdditive = "Ich hab dich lieb!"
          customColor = "#FF0000"
          customValue = 4.09
          return customAdditive, customValue, customColor
          
