import streamlit as st
from openai import OpenAI

st.title("🎓 Akademik Danışman AI")

# Senin o muhteşem promptun buraya sistem mesajı olarak giriyor
SYSTEM_PROMPT = """Sen, yüksek lisans öğrencilerine tez konusu ve araştırma sorusu belirleme konusunda rehberlik eden... (Buraya senin tam promptunu yapıştır)"""

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.messages.append({"role": "assistant", "content": "Merhaba! Ben Akademik Danışman AI. Şu an akademik dünyada seni en çok rahatsız eden o spesifik olgu nedir?"})

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)