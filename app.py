import streamlit as st
import google.generativeai as genai

# 1. Sayfa Ayarları
st.set_page_config(page_title="Akademik Danışman AI", page_icon="🎓")

st.title("🎓 Akademik Danışman AI")
st.caption("Gemini 3 Flash Altyapısı ile Tez Asistanı")

# Senin Orijinal Süper Promptun
SYSTEM_PROMPT = """
Sen, yüksek lisans öğrencilerine tez konusu ve araştırma sorusu belirleme konusunda rehberlik eden, metodoloji uzmanı bir Akademik Danışman AI'sısın. Görevin, öğrenci en özgün ve uygulanabilir araştırma sorusuna ulaşana kadar ona Sokratik bir yöntemle rehberlik etmektir.

Lütfen şu 12 tekniklik protokolü tavizsiz uygula:
1. Step-Back: Doğrudan başlık bulmaya çalışma... (Promptunun devamını buraya eksiksiz koy)
"""

# 2. API Yapılandırması
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Lütfen Streamlit Secrets kısmına GEMINI_API_KEY ekleyin!")
    st.stop()

# 3. Model Kurulumu (Gemini 3 Flash için düzenlendi)
@st.cache_resource
def load_gemini_3():
    # Model ismini tam olarak 2026 standartlarına, yani Gemini 3 Flash'a göre güncelledik
    return genai.GenerativeModel(
        model_name='gemini-3-flash', 
        system_instruction=SYSTEM_PROMPT
    )

try:
    model = load_gemini_3()
except Exception:
    # Eğer kısa isim hata verirse tam yolunu dener
    model = genai.GenerativeModel(model_name='models/gemini-3-flash')

# 4. Sohbet Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])
    
    initial_text = "Merhaba! Ben Akademik Danışman AI. Gemini 3 Flash gücüyle yanındayım. İlgi duyduğunuz alan nedir?"
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

# Mesajları Ekrana Bas
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Kullanıcı Girişi
if prompt := st.chat_input("Mesajınızı buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Gemini 3 Flash çok hızlı yanıt verir
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
