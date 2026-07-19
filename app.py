import streamlit as st
import numpy as np
import folium
import tempfile

# ==========================================
# 1. КОНФИГУРАЦИЯ И СТИЛИЗАЦИЯ (CSS)
# ==========================================
st.set_page_config(page_title="AquaScan Астана", layout="wide")

st.markdown("""
<style>
    /* Фон страницы и сайдбара */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Стили для метрик и карточек */
    div[data-testid="metric-container"] {
        background-color: #1E2430;
        border: 1px solid #4CAF50;
        padding: 15px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    /* Кнопки */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
        padding: 12px 20px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: scale(1.02);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ФУНКЦИЯ ГЕНЕРАЦИИ СЕГМЕНТИРОВАННОЙ КАРТЫ
# ==========================================
def generate_ishim_map():
    """Создает карту Астаны с полилиниями русла Ишима, разбитыми на классы."""
    # Центрируем карту по средним координатам русла Ишима в Астане
    m = folium.Map(location=[51.166, 71.425], zoom_start=13, control_scale=True)
    
    # Координаты точек русла реки Ишим
    p1 = [51.180, 71.405]
    p2 = [51.170, 71.415]
    p3 = [51.160, 71.430]
    p4 = [51.155, 71.450]
    
    # Сегмент 1: Чистая вода (Синий)
    folium.PolyLine(
        locations=[p1, p2],
        color="blue",
        weight=8,
        opacity=0.85,
        popup=folium.Popup("<b>Статус:</b> Чистая вода<br><b>Индекс NDWI:</b> Высокий", max_width=200)
    ).add_to(m)
    
    # Сегмент 2: Нефтяное загрязнение (Красный)
    folium.PolyLine(
        locations=[p2, p3],
        color="red",
        weight=8,
        opacity=0.85,
        popup=folium.Popup("<b>Статус:</b> Компоненты нефти<br><b>Вероятность:</b> 12.5%", max_width=200)
    ).add_to(m)
    
    # Сегмент 3: Водоросли / Цветение (Желтый)
    folium.PolyLine(
        locations=[p3, p4],
        color="yellow",
        weight=8,
        opacity=0.85,
        popup=folium.Popup("<b>Статус:</b> Активное цветение<br><b>Плотность:</b> 8.2%", max_width=200)
    ).add_to(m)
    
    return m

# ==========================================
# 3. ИНТЕРФЕЙС БОКОВОЙ ПАНЕЛИ (SIDEBAR)
# ==========================================
st.sidebar.header("📁 Параметры AquaScan")
st.sidebar.info("📍 Локация: г. Астана, р. Ишим")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Настройка алертов")
email_input = st.sidebar.text_input("Email для экстренных уведомлений:", value="eco-officer@astana.kz")
alert_threshold = st.sidebar.slider("Порог тревоги (% аномалий):", min_value=0, max_value=100, value=10)

# ==========================================
# 4. ЛОГИКА ГЛАВНОГО ЭКРАНА
# ==========================================
st.title("🛰️ AquaScan — Мониторинг акваторий")
st.caption("Система оперативного анализа экологического состояния водных ресурсов")

# Кнопка запуска анализа по центру
st.markdown("### Экспресс-анализ спутниковых снимков")
run_analysis = st.button("🚀 ЗАПУСТИТЬ АНАЛИЗ")

st.markdown("---")

# Проверка состояния: нажал ли пользователь кнопку
if run_analysis:
    # Имитация работы ML-модели
    with st.spinner("Загрузка растровых спектральных данных и запуск ML-модели..."):
        # 1. Вывод метрик в 3 колонки
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Нефтяное загрязнение", value="12.5%", delta="⚠️ Выше нормы")
        with col2:
            st.metric(label="Цветение водорослей", value="8.2%", delta="🌱 Умеренно")
        with col3:
            st.metric(label="Уверенность модели", value="95.0%", delta="🎯 Точно")
            
        # 2. Триггер алертов на основе введенных в сайдбаре настроек
        # Так как загрязнение нефти (12.5%) + водоросли (8.2%) = ~20.7% общих аномалий
        total_anomalies = 20.7
        if total_anomalies > alert_threshold:
            st.warning(f"⚠️ Обнаружен уровень аномалий {total_anomalies}% (Порог: {alert_threshold}%)!")
            st.success(f"📧 Сгенерирован рапорт. Уведомление отправлено на почту **{email_input}**")

        # 3. Генерация и отображение интерактивной карты русла реки
        st.markdown("### Карта векторов загрязнения русла реки Ишим")
        map_object = generate_ishim_map()
        
        # Рендеринг Folium во временный HTML-файл для встраивания в Streamlit
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            map_object.save(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_string = f.read()
        st.components.v1.html(html_string, height=500)
        
        st.markdown("**Легенда русла:** 🔵 Чистая вода | 🔴 Нефтяные пленки | 🟡 Очаги размножения водорослей")
        st.info("💡 Нажмите на цветные участки реки на карте, чтобы увидеть подробную информацию по сегменту.")

else:
    # Состояние по умолчанию до клика по кнопке
    st.info("ℹ️ **Ожидание снимка.** Нажмите кнопку выше, чтобы запустить процедуру сегментации водного объекта.")
