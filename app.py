import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Akademik Danışman AI", page_icon="🎓", layout="centered")

# Stil Ayarları (Daha şık bir görünüm için)
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Akademik Danışman AI")
st.caption("Yüksek Lisans Tez ve Araştırma Sorusu Mimarı")

# 1. Prompt Tanımı (Senin Protokolün)
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
"""

# 2. Gemini API Yapılandırması
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Hata: Streamlit Secrets kısmında 'GEMINI_API_KEY' bulunamadı.")
    st.stop()

# Model Kurulumu (Hata payını azaltmak için flash modelini kullanıyoruz)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# 3. Sohbet Geçmişi Yönetimi (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Gemini'nin kendi chat objesini başlatıyoruz
    st.session_state.chat = model.start_chat(history=[])
    
    # İlk mesaj (Başlatma sorusu)
    initial_text = "Merhaba! Ben Akademik Danışman AI. Şu an akademik dünyada seni en çok rahatsız eden, eksik bulduğun veya 'bunun doğrusu aslında şu olabilir' dediğin o spesifik olgu nedir? Önce biraz ilgi alanlarından bahsedebilirsin."
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

# 4. Mesajları Ekranda Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Kullanıcı Etkileşimi
if prompt := st.chat_input("Mesajınızı buraya yazın..."):
    # Kullanıcı mesajını ekrana bas ve hafızaya al
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini'den yanıt al
    with st.chat_message("assistant"):
        try:
            # Yanıt gelene kadar bir yükleme simgesi gösterir
            with st.spinner("Düşünüyorum..."):
                response = st.session_state.chat.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Bir hata oluştu. Lütfen API anahtarınızı veya internetinizi kontrol edin. Hata: {e}")
