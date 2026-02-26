import streamlit as st
import google.generativeai as genai

# 1. Sayfa Ayarları
st.set_page_config(page_title="Akademik Danışman AI", page_icon="🎓")

st.title("🎓 Akademik Danışman AI")
st.caption("Sokratik Yöntemle Tez ve Araştırma Sorusu Mimarı")

# 2. Senin Süper Promptun
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

# 3. API Yapılandırması
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets bulunamadı!")
    st.stop()

# 4. Model Seçimi (404 Hatasını Önleyen Mekanizma)
# Bu liste içindeki modellerden hangisi sisteminde varsa onu seçecek
model_names = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro"]
model = None

for m_name in model_names:
    try:
        model = genai.GenerativeModel(model_name=m_name)
        # Modelin gerçekten çalışıp çalışmadığını test ediyoruz
        model.generate_content("test") 
        break 
    except:
        continue

if model is None:
    st.error("Üzgünüm, Google API modellerine şu an ulaşılamıyor. Lütfen API anahtarınızı kontrol edin.")
    st.stop()

# 5. Sohbet Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])
    
    # Sisteme kim olduğunu hatırlat (Hata vermemesi için güvenli mod)
    try:
        st.session_state.chat.send_message(f"TALİMAT: {SYSTEM_PROMPT}")
    except:
        pass
        
    initial_text = "Merhaba! Ben Akademik Danışman AI. Akademik dünyada seni en çok rahatsız eden o spesifik olgu nedir?"
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

for msg in st.session_state.messages:
    if msg["role"] != "system": # Sistem talimatını ekranda gösterme
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 6. Kullanıcı Girişi
if user_input := st.chat_input("Buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(user_input)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata: {e}")
