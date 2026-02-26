import streamlit as st
import google.generativeai as genai

st.title("🎓 Akademik Danışman AI (Gemini)")

# Senin muhteşem promptun
SYSTEM_PROMPT = """Sen, yüksek lisans öğrencilerine tez konusu ve araştırma sorusu belirleme konusunda rehberlik eden... (Buraya tam promptunu yapıştır)"""

# Gemini Ayarı
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])
    # İlk karşılama
    initial_msg = "Merhaba! Ben Akademik Danışman AI. Şu an akademik dünyada seni en çok rahatsız eden o spesifik olgu nedir?"
    st.session_state.messages.append({"role": "assistant", "content": initial_msg})

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = st.session_state.chat.send_message(prompt)
    msg = response.text
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
