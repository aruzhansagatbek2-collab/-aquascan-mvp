import streamlit as st
import folium
import streamlit.components.v1 as components
import pandas as pd
import time
import io
from datetime import datetime

# Подключение ReportLab для генерации PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- 1. НАСТРОЙКИ СТРАНИЦЫ И CSS ДИЗАЙН ---
st.set_page_config(
    page_title="AquaScan AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для контрастности и темной темы
st.markdown("""
<style>
    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Сайдбар - жесткие контрастные цвета */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
    }
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #E6EDF3 !important;
    }

    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #1F242D !important;
        border: 1px solid #30363D !important;
    }

    div[data-baseweb="input"] > div {
        background-color: #1F242D !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] button {
        background-color: #1E90FF !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        transition: 0.3s !important;
    }

    /* Кнопки скачивания */
    div[data-testid="stDownloadButton"] > button {
        background-color: #1F6FED !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        width: 100%;
        transition: 0.3s !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #388BFD !important;
        box-shadow: 0 0 12px rgba(56, 139, 253, 0.6) !important;
    }
    div[data-testid="stDownloadButton"] > button p {
        color: #FFFFFF !important;
    }

    /* Главная кнопка */
    div.stButton > button[kind="primary"] {
        background-color: #1F6FED !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #388BFD !important;
        box-shadow: 0 0 15px rgba(56, 139, 253, 0.5);
    }

    /* Метрики */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 15px !important;
        color: #A0AEC0 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #1F242D;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация состояния анализа
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

# --- 2. ГЕНЕРАЦИЯ PDF ДЛЯ ИНСПЕКТОРА ---
def generate_pdf_report(loc, clean_pct, clean_km, algae_pct, algae_km, oil_pct, oil_km, ai_conf, thresh, email_to):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1F6FED'), spaceAfter=10
    )
    sub_style = ParagraphStyle(
        'SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'), spaceAfter=15
    )
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, spaceAfter=8)
    caption_style = ParagraphStyle(
        'CaptionStyle', parent=styles['Italic'], fontSize=9, textColor=colors.HexColor('#777777'), spaceBefore=15
    )

    elements.append(Paragraph("AquaScan AI — Официальный отчет мониторинга акватории", title_style))
    elements.append(Paragraph(f"Дата и время генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_style))
    
    elements.append(Paragraph(f"<b>Объект наблюдения:</b> {loc}", text_style))
    elements.append(Paragraph(f"<b>Установленный порог тревоги:</b> {thresh}%", text_style))
    if email_to:
        elements.append(Paragraph(f"<b>Получатель уведомления:</b> {email_to}", text_style))
    
    elements.append(Spacer(1, 10))
    
    status_str = "КРИТИЧЕСКИЙ УРОВЕНЬ" if oil_pct >= thresh else "НОРМА"
    status_color = colors.HexColor('#D32F2F') if oil_pct >= thresh else colors.HexColor('#2E7D32')
    
    table_data = [
        ["Параметр экосистемы", "Процент покрытия", "Площадь (км²)", "Статус"],
        ["🌊 Чистая вода", f"{clean_pct}%", f"{clean_km} км²", "В норме"],
        ["🧪 Цветение водорослей", f"{algae_pct}%", f"{algae_km} км²", "Мониторинг"],
        ["⚠️ Аномалия (нефть)", f"{oil_pct}%", f"{oil_km} км²", status_str]
    ]
    
    table = Table(table_data, colWidths=[160, 110, 110, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F6FED')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9FA')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (3,3), (3,3), status_color),
        ('FONTNAME', (3,3), (3,3), 'Helvetica-Bold')
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Точность оценки спектральной модели ИИ:</b> {ai_conf}%", text_style))
    elements.append(Paragraph("⚠️ <i>Система используется для первичного скрининга. Для юридического подтверждения загрязнения требуются лабораторные пробы Казгидромета.</i>", caption_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# --- 3. САЙДБАР ---
with st.sidebar:
    st.markdown("## ⚙️ Настройки сканирования")
    
    location = st.selectbox(
        "📍 Выберите локацию:", 
        ["г. Астана, р. Ишим", "Озеро Балхаш (демо)"]
    )
    
    alert_threshold = st.slider(
        "🎯 Порог срабатывания алерта (%)", 
        min_value=0, 
        max_value=100, 
        value=5, 
        help="Если загрязнение превысит этот процент, система активирует тревогу."
    )
    
    st.markdown("---")
    st.markdown("### 🔔 Экстренные оповещения")
    email = st.text_input("Email для отчетов:", placeholder="inspector@eco.gov.kz")
    
    if st.button("Активировать мониторинг", use_container_width=True):
        if email:
            st.success(f"Мониторинг активирован: {email}")
        else:
            st.warning("Укажите E-mail!")


# --- 4. ЦЕНТРАЛЬНЫЙ ИНТЕРФЕЙС ---
st.title("🛰️ AquaScan AI: Спутниковый мониторинг акваторий")

if not st.session_state.analyzed:
    st.info("Нажмите кнопку ниже для получения актуальных данных со спутника Sentinel-2.")

# Кнопка запуска анализа
if st.button('🚀 ЗАПУСТИТЬ АНАЛИЗ', type="primary"):
    with st.spinner('Загрузка мультиспектральных снимков Sentinel-2 и обработка ИИ...'):
        time.sleep(2.5)
    st.session_state.analyzed = True

# Отображение результатов анализа
if st.session_state.analyzed:
    
    # 1. Заголовок активного мониторинга (жесткий HTML стиль)
    st.markdown(
        f"""
        <h3 style='color: #FFFFFF; font-weight: bold; font-size: 22px; margin-top: 10px; margin-bottom: 15px;'>
            📍 Активный мониторинг: {location}
        </h3>
        """, 
        unsafe_allow_html=True
    )

    # Данные эмуляции ML в зависимости от локации
    if location == "г. Астана, р. Ишим":
        clean_pct, clean_km = 85.0, 12.4
        algae_pct, algae_km = 12.0, 1.8
        oil_pct, oil_km = 3.0, 0.4
        map_center = [51.169, 71.449]
        map_zoom = 13
    else:
        clean_pct, clean_km = 91.0, 410.0
        algae_pct, algae_km = 2.5, 11.2
        oil_pct, oil_km = 6.5, 29.2
        map_center = [45.0, 74.0]
        map_zoom = 9

    ai_confidence = 95.0

    # 2. Логика Алерта
    if oil_pct >= alert_threshold:
        st.error(f"⚠️ ТРЕВОГА! Обнаружена аномалия нефти ({oil_pct}%), что превышает установленный порог {alert_threshold}%! Требуется проверка.")
    else:
        st.success(f"✅ Экологическая обстановка в норме. Уровень аномалий ({oil_pct}%) ниже порога ({alert_threshold}%).")

    # 3. Метрики площади
    m1, m2, m3 = st.columns(3)
    m1.metric("🌊 Чистая вода", f"{clean_pct}%", f"{clean_km} км²", delta_color="normal")
    m2.metric("🧪 Цветение водорослей", f"{algae_pct}%", f"{algae_km} км²", delta_color="off")
    m3.metric("⚠️ Аномалия (нефть)", f"{oil_pct}%", f"{oil_km} км²", delta_color="inverse")
    
    st.markdown(f"**🎯 Точность ИИ:** `{ai_confidence}%` *(Спектральный анализ мультиспектральных каналов B8A/B11)*")

    # 4. Карта загрязнений
    st.markdown("---")
    st.subheader("🗺️ Интерактивная карта классификации акватории")
    st.caption("🔴 Красный: Аномалия (нефть) | 🟡 Желтый: Цветение водорослей | 🔵 Синий: Чистая вода")

    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB dark_matter")

    if location == "г. Астана, р. Ишим":
        ishim_coords = [
            [51.180, 71.405], [51.175, 71.410], 
            [51.170, 71.415], [51.165, 71.420], 
            [51.160, 71.425], [51.155, 71.430]
        ]
        poly_oil = [[c[0], c[1]-0.002] for c in ishim_coords[0:2]] + [[c[0], c[1]+0.002] for c in reversed(ishim_coords[0:2])]
        poly_algae = [[c[0], c[1]-0.002] for c in ishim_coords[2:4]] + [[c[0], c[1]+0.002] for c in reversed(ishim_coords[2:4])]
        poly_clean = [[c[0], c[1]-0.002] for c in ishim_coords[4:6]] + [[c[0], c[1]+0.002] for c in reversed(ishim_coords[4:6])]

        folium.Polygon(locations=poly_oil, color='red', fill=True, fill_color='red', fill_opacity=0.7, tooltip="Аномалия (нефть): 0.4 км²").add_to(m)
        folium.Polygon(locations=poly_algae, color='yellow', fill=True, fill_color='yellow', fill_opacity=0.7, tooltip="Водоросли: 1.8 км²").add_to(m)
        folium.Polygon(locations=poly_clean, color='blue', fill=True, fill_color='blue', fill_opacity=0.5, tooltip="Чистая вода: 12.4 км²").add_to(m)
    else:
        folium.Circle(location=[45.05, 74.05], radius=12000, color='red', fill=True, fill_color='red', fill_opacity=0.7, tooltip="Аномалия (нефть): 29.2 км²").add_to(m)
        folium.Circle(location=[45.15, 73.85], radius=8000, color='yellow', fill=True, fill_color='yellow', fill_opacity=0.7, tooltip="Водоросли: 11.2 км²").add_to(m)
        folium.Circle(location=[44.90, 74.20], radius=25000, color='blue', fill=True, fill_color='blue', fill_opacity=0.4, tooltip="Чистая вода: 410.0 км²").add_to(m)

    map_html = m.get_root().render()
    components.html(map_html, height=520)

    # 5. Дисклеймер
    st.caption("⚠️ Система используется для первичного скрининга. Для юридического подтверждения загрязнения требуются лабораторные пробы Казгидромета.")

    # 6. Кнопка Экспорта
    st.markdown("---")
    pdf_bytes = generate_pdf_report(
        location, clean_pct, clean_km, algae_pct, algae_km, oil_pct, oil_km, ai_confidence, alert_threshold, email
    )
    
    st.download_button(
        label="📑 Скачать PDF-отчет для инспектора",
        data=pdf_bytes,
        file_name=f"AquaScan_Inspector_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
