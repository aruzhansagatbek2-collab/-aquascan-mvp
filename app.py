import streamlit as st
import folium
import time

# --- НАСТРОЙКА СТРАНИЦЫ И CSS ---
st.set_page_config(page_title="AquaScan AI", layout="wide")

st.markdown("""
<style>
    /* Общий фон приложения и сайдбара */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .css-1d391kg, .css-1lcbmhc {
        background-color: #161B22;
    }
    
    /* Текст в сайдбаре */
    .stSidebar .stMarkdown, .stSidebar .stSelectbox, .stSidebar .stSlider, .stSidebar .stTextInput {
        color: #FFFFFF !important;
    }
    
    /* Карточки метрик (цифры) */
    div[data-testid="metric-container"] {
        background-color: #1E2430;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="metric-container"] label {
        color: #8b949e !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; /* Делаем цифры ярко-белыми */
        font-size: 32px;
    }

    /* Кнопки */
    .stButton > button {
        background-color: #1E90FF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #3da0ff;
    }
    
    /* Кнопки скачивания */
    .stDownloadButton > button {
        background-color: #1E90FF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stDownloadButton > button:hover {
        background-color: #3da0ff;
    }
</style>
""", unsafe_allow_html=True)


# --- САЙДБАР ---
st.sidebar.title("⚙️ Настройки сканирования")

location = st.sidebar.selectbox("📍 Выберите локацию:", ["г. Астана, р. Ишим", "Озеро Балхаш (демо)"])
threshold = st.sidebar.slider("🎯 Порог срабатывания алерта (%)", 0, 100, 5, format="%d%%")

st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Уведомления")
email = st.sidebar.text_input("Email для экстренных отчетов:")

if st.sidebar.button("Активировать мониторинг"):
    if email:
        st.sidebar.success(f"✅ Оповещения включены для {email}")
    else:
        st.sidebar.warning("⚠️ Введите Email для получения алертов")


# --- ОСНОВНОЙ ЭКРАН ---
st.title("🛰️ AquaScan AI: Спутниковый мониторинг")

status_placeholder = st.empty()
status_placeholder.info("⏳ Ожидание запуска анализа...")

if st.button("🚀 ЗАПУСТИТЬ АНАЛИЗ", type="primary"):
    status_placeholder.empty()
    
    # Имитация работы сервера
    with st.spinner('⏳ Спутник Sentinel-2 передает данные... ИИ обрабатывает каналы...'):
        time.sleep(2.5)
    
    # Эмуляция ML-расчетов
    oil = 12.5
    algae = 8.2
    confidence = 95.0
    date_str = "20.07.2026"

    st.success("✅ Анализ снимков Sentinel-2 успешно завершен!")

    # --- ИСПРАВЛЕНИЕ: ЯРКАЯ БЕЛАЯ НАДПИСЬ ЛОКАЦИИ ---
    if location == "г. Астана, р. Ишим":
        loc_text = "г. Астана, р. Ишим"
        map_center = [51.169, 71.449]
        poly_points = [[51.180, 71.405], [51.175, 71.410], [51.170, 71.415], [51.165, 71.420], [51.160, 71.425], [51.155, 71.430]]
    else:
        loc_text = "Озеро Балхаш"
        map_center = [45.0, 74.0]
        poly_points = [[45.05, 74.05], [45.04, 74.08], [45.03, 74.12], [45.02, 74.15], [45.01, 74.18], [45.00, 74.20]]

    st.markdown(f"""
    <h3 style='color: #FFFFFF; font-weight: bold; margin-top: 10px; margin-bottom: 10px;'>
        📍 Активный мониторинг: {loc_text}
    </h3>
    """, unsafe_allow_html=True)

    # Логика порога
    if oil >= threshold:
        st.error(f"⚠️ ТРЕВОГА! Загрязнение нефтью ({oil}%) превысило порог в {threshold}%! Срочно проверьте почту!")
        if not email:
            st.warning("⚠️ Алерт не отправлен, так как Email не указан в настройках.")
    else:
        st.success(f"✅ Экологическая обстановка в норме. Загрязнение ({oil}%) ниже порога ({threshold}%).")

    # Метрики
    col1, col2, col3 = st.columns(3)
    col1.metric("🛢️ Нефтепродукты", f"{oil}%", "+2.1% с прошлого снимка")
    col2.metric("🧪 Цветение водорослей", f"{algae}%", "-0.5%")
    col3.metric("🎯 Точность ИИ", f"{confidence}%", "На основе уверенности модели")

    # Метаданные снимка
    st.caption(f"🛰️ Источник: Sentinel-2 L2A | Дата съемки: {date_str} | Облачность: <5% | Разрешение: 10м/пикс")

    # Карта
    st.subheader("🗺️ Интерактивная карта загрязнений")
    st.markdown("🔴 Красный: Нефтепродукты | 🟡 Желтый: Водоросли | 🔵 Синий: Чистая вода")

    m = folium.Map(location=map_center, zoom_start=12, tiles='CartoDB dark_matter')

    # Рисуем эмуляцию реки с разными загрязнениями
    folium.Polygon(
        locations=[poly_points[0], poly_points[1], poly_points[2]],
        color="red", fill=True, fill_color="red", fill_opacity=0.6, popup="Нефтяное загрязнение"
    ).add_to(m)

    folium.Polygon(
        locations=[poly_points[2], poly_points[3], poly_points[4]],
        color="yellow", fill=True, fill_color="yellow", fill_opacity=0.6, popup="Цветение водорослей"
    ).add_to(m)

    folium.Polygon(
        locations=[poly_points[4], poly_points[5], poly_points[0]],
        color="blue", fill=True, fill_color="blue", fill_opacity=0.6, popup="Чистая вода"
    ).add_to(m)

    # Отображение карты
    folium_map_html = m._repr_html_()
    st.components.v1.html(folium_map_html, width=800, height=550)

    # Экспорт отчетов
    st.markdown("---")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.download_button(
            label="📄 Скачать отчет (PDF)",
            data=f"Эмуляция PDF отчета.\nДата: {date_str}\nНефть: {oil}%\nВодоросли: {algae}%\nТочность: {confidence}%",
            file_name=f"AquaScan_Report_{date_str}.pdf",
            mime="application/pdf"
        )
    
    with col_exp2:
        csv_data = f"Дата,Локация,Нефть,Водоросли,Точность\n{date_str},{loc_text},{oil},{algae},{confidence}"
        st.download_button(
            label="📊 Скачать данные (CSV)",
            data=csv_data,
            file_name=f"AquaScan_Data_{date_str}.csv",
            mime="text/csv"
        )
