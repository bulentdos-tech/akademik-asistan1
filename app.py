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

# 4. Model Kurulumu (Hata veren Flash yerine en stabil olan 'gemini-pro'yu seçtik)
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-pro", # Bu isim en stabil olanıdır
        system_instruction=None # gemini-pro doğrudan sistem talimatını desteklemeyebilir, aşağıda düzelteceğiz
    )

model = load_model()

# 5. Sohbet Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Sistem promptunu konuşmanın en başına gizli bir şekilde ekliyoruz
    st.session_state.chat = model.start_chat(history=[])
    # İlk mesajda sistem promptunu göndererek AI'ya kim olduğunu öğretiyoruz
    st.session_state.chat.send_message(f"SİSTEM TALİMATI: {SYSTEM_PROMPT}\n\nLütfen kendini tanıt ve başla.")
    
    initial_text = "Merhaba! Ben Akademik Danışman AI. Akademik dünyada seni en çok rahatsız eden, eksik bulduğun o spesifik olgu nedir?"
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

# Mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. Kullanıcı Girişi
if user_input := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(user_input)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
