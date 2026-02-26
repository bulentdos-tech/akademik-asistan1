import streamlit as st
import google.generativeai as genai

# 1. Sayfa Ayarları
st.set_page_config(page_title="Akademik Danışman AI", page_icon="🎓")

st.title("🎓 Akademik Danışman AI")
st.caption("Gemini 3 Altyapısı ile Akıllı Tez Asistanı")

# Senin Süper Promptun
SYSTEM_PROMPT = """Sen, yüksek lisans öğrencilerine tez konusu ve araştırma sorusu belirleme konusunda rehberlik eden bir Akademik Danışman AI'sısın... (Lütfen buraya 12 maddelik promptunu yapıştır)"""

# 2. API Yapılandırması
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets kısmında GEMINI_API_KEY bulunamadı!")
    st.stop()

# 3. Model Bulma Mekanizması (Hata almamak için dinamik seçim)
@st.cache_resource
def get_best_model():
    try:
        # Mevcut modelleri listele
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Öncelik sırasına göre Gemini 3 varyantlarını ara
        for target in ['models/gemini-3-flash', 'models/gemini-3-pro', 'gemini-3-flash']:
            if target in models:
                return target
        
        # Eğer hiçbiri yoksa listedeki ilk modeli al (En güvenli yol)
        return models[0] if models else None
    except Exception:
        # Liste alınamazsa manuel deneme yap
        return 'gemini-3-flash'

best_model_name = get_best_model()

# 4. Model Kurulumu
if best_model_name:
    model = genai.GenerativeModel(
        model_name=best_model_name,
        system_instruction=SYSTEM_PROMPT
    )
else:
    st.error("Erişilebilir model bulunamadı. Lütfen API anahtarınızı kontrol edin.")
    st.stop()

# 5. Sohbet Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])
    
    initial_text = "Merhaba! Ben Akademik Danışman AI. Gemini 3'ün güncel gücüyle yanındayım. İlgi duyduğun alanı sorarak başlayabiliriz."
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

# Mesajları Görüntüle
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Kullanıcı Girişi
if user_input := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
