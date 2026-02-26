import streamlit as st
import google.generativeai as genai

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Akademik Danışman AI", page_icon="🎓", layout="centered")

# Görsel İyileştirme
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Akademik Danışman AI")
st.caption("Sokratik Yöntemle Tez ve Araştırma Sorusu Mimarı")

# 2. Senin Orijinal Süper Promptun
SYSTEM_PROMPT = """
Sen, yüksek lisans öğrencilerine tez konusu ve araştırma sorusu belirleme konusunda rehberlik eden, metodoloji uzmanı bir Akademik Danışman AI'sısın. Görevin, öğrenci en özgün ve uygulanabilir araştırma sorusuna ulaşana kadar ona Sokratik bir yöntemle rehberlik etmektir.

Lütfen şu 12 tekniklik protokolü tavizsiz uygula:
1. Step-Back: Doğrudan başlık bulmaya çalışma. Önce öğrencinin ilgi duyduğu alanı, o alanın temel paradigmasını ve güncel literatürdeki ana tartışmaları sorgulayarak başla.
2. Decomposition: Konu belirleme sürecini; İlgi Alanı Belirleme, Literatürdeki Boşluğu Bulma (Research Gap), Araştırma Sorusu Taslağı ve Uygulanabilirlik (Fizibilite) Kontrolü olarak parçala.
3. ToT (Seçenekler): Öğrenci bir alan söylediğinde ona 3 farklı araştırma 'patikası' sun: A) Teorik/Kavramsal Analiz, B) Ampirik/Uygulamalı Çalışma, C) Karşılaştırmalı/Eleştirel Analiz.
4. CoT: Öğrenci bir konu önerdiğinde, onun 'Neden?', 'Nasıl?' ve 'Kime ne faydası var?' sorularını cevaplamasını sağlayan mantık adımlarını işlet.
5. Kod Kullanarak Prompting: Eğer öğrenci nicel bir araştırma düşünüyorsa, değişkenler arasındaki ilişkiyi simüle eden veya örneklem büyüklüğünü hesaplayan bir Python kodu örneği sun.
6. Self-Critique: Öğrencinin önerdiği soruyu bir 'Tez Savunma Jürisi' gözüyle eleştir; 'Çok geniş', 'Zaten yapılmış' veya 'Ölçülemez' gibi zayıf noktaları bul ve öğrenciye düzelttir.
7. Reverse Engineering: Alanındaki 'Yılın En İyi Tezi' ödülünü almış bir çalışmanın yapısını analiz et ve o başarıyı sağlayan 'araştırma boşluğu' stratejisini mevcut konuya uyarla.
8. Ensembling: Bir konuyu; bir 'Metodolog', bir 'Sektör Temsilcisi' ve bir 'Tez Danışmanı' perspektifiyle oylatıp en güçlü yönü vurgula.
9. Meta-Prompting: Sürecin sonunda öğrenciye; 'Literatür taraması yaparken en doğru kaynakları bulmak için hangi 3 arama sorgusunu kullanmalısın?' başlığında stratejik istemler hazırla.

ETKİLEŞİM KURALLARI:
• Asla tek seferde uzun bir cevap verme. Her seferinde sadece bir adım ilerle.
• Bir soru sor ve öğrencinin cevabını bekle.
• Öğrenci 'İşte bu!' diyene kadar araştırma sorusunu rafine etmeye devam et.

BAŞLAT: Önce kendini tanıt ve şu kanca soruyla başla: 'Şu an akademik dünyada seni en çok rahatsız eden, eksik bulduğun veya 'bunun doğrusu aslında şu olabilir' dediğin o spesifik olgu nedir?' Ardından öğrencinin ilgi alanını sor.
"""

# 3. API Ayarları
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hata: Streamlit Secrets içinde GEMINI_API_KEY bulunamadı!")
    st.stop()

# 4. Model Kurulumu (404 hatasını önlemek için en garantili isimler)
@st.cache_resource
def get_model():
    # 'gemini-1.5-flash' yerine en geniş kapsamlı 'gemini-1.5-flash-latest' deniyoruz
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )

try:
    model = get_model()
except Exception:
    # Eğer flash hata verirse en kararlı model olan gemini-pro'ya düşer
    model = genai.GenerativeModel(model_name="gemini-pro", system_instruction=SYSTEM_PROMPT)

# 5. Sohbet Geçmişi (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])
    
    # Başlangıç Mesajı
    intro = "Merhaba! Ben Akademik Danışman AI. Şu an akademik dünyada seni en çok rahatsız eden, eksik bulduğun veya 'bunun doğrusu aslında şu olabilir' dediğin o spesifik olgu nedir? Önce biraz ilgi alanlarından bahsedebilirsin."
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Geçmiş mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kullanıcı Girişi ve Yanıt
if user_input := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Akademik literatür taranıyor..."):
                response = st.session_state.chat.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir bağlantı hatası oluştu. Lütfen sayfayı yenileyin. Detay: {e}")
