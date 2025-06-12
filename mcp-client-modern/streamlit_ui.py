import streamlit as st
import asyncio
from client import run_claude_chat

st.set_page_config(page_title="Claude Chat", layout="centered")
st.title("🤖 Claude E-Ticaret Asistanı")

# Oturum durumu için geçmiş mesajları kontrol et
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_product_json" not in st.session_state:
    st.session_state.last_product_json = None

# Geçmiş sohbetleri göster
for role, msg in st.session_state.chat_history:
    st.chat_message(role).markdown(msg)

# Önceki başarılı JSON sonuç varsa kart olarak göster
if st.session_state.last_product_json:
    for product in st.session_state.last_product_json:
        st.markdown(f"### 🛍️ {product['title']}")
        for v in product['variants']:
            st.image(v['image_url'], width=200)
            st.markdown(f"**🎨 Renk:** {v['color']}  ")
            st.markdown(f"**📐 Beden:** {v['size']}  ")
            st.markdown(f"**📦 Stok:** {v['inventory']}  ")
            st.markdown("---")

# Yeni mesaj kutusu
if prompt := st.chat_input("Claude'a bir şey sor..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.spinner("Claude düşünüyor..."):
        result = asyncio.run(run_claude_chat(prompt))

    # Eğer liste/dict geldiyse ürün olarak al, değilse metin olarak göster
    if isinstance(result, (list, dict)):
        st.session_state.last_product_json = result if isinstance(result, list) else [result]
        st.rerun()
    else:
        st.chat_message("assistant").markdown(result)
        st.session_state.chat_history.append(("assistant", result))
        st.session_state.last_product_json = None
