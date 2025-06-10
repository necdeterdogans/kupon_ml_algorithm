# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Mevcut kodlarınızı import edin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kupon_mvp import KuponAnalyzer
from api_integration import EnhancedKuponAnalyzer
from ml_algorithm import MLKuponAnalyzer

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="⚽ Kupon Analiz Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1e88e5;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .confidence-high {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .confidence-medium {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .confidence-low {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<h1 class="main-header">⚽ Kupon Analiz Sistemi</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎯 Analiz Seçenekleri")

# Analiz tipi seçimi
analysis_type = st.sidebar.selectbox(
    "Analiz Tipi",
    ["Tekli Maç Analizi", "Kupon Analizi", "Takım Karşılaştırması", "Geçmiş Performans"]
)

# Türk ligleri takımları
turkish_teams = [
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", 
    "Başakşehir", "Konyaspor", "Sivasspor", "Alanyaspor",
    "Kasımpaşa", "Gaziantep FK", "Hatayspor", "Antalyaspor"
]

european_teams = [
    "Real Madrid", "Barcelona", "Manchester United", "Liverpool",
    "Bayern Munich", "PSG", "Juventus", "Chelsea", "Arsenal"
]

all_teams = turkish_teams + european_teams

# Analiz tipine göre arayüz
if analysis_type == "Tekli Maç Analizi":
    st.header("🥅 Tekli Maç Analizi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Ev Sahibi Takım")
        home_team = st.selectbox("Ev Sahibi", all_teams, key="home")
        
    with col2:
        st.subheader("✈️ Deplasman Takımı")
        away_team = st.selectbox("Deplasman", all_teams, key="away")
    
    # Bahis tipi seçimi
    bet_type = st.selectbox("Bahis Tipi", ["1X2", "Alt/Üst 2.5 Gol", "Çifte Şans"])
    
    # Analiz butonu
    if st.button("🔍 Analiz Et", type="primary"):
        if home_team != away_team:
            # Tüm analizleri yap
            col1, col2, col3 = st.columns(3)
            
            # MVP Analizi
            analyzer_mvp = KuponAnalyzer()
            result_mvp = analyzer_mvp.analyze_match(home_team, away_team, bet_type)
            
            # API Analizi
            analyzer_api = EnhancedKuponAnalyzer()
            result_api = analyzer_api.analyze_match_with_api(home_team, away_team)
            
            # ML Analizi
            analyzer_ml = MLKuponAnalyzer()
            try:
                analyzer_ml.load_models()
                home_stats = {'attack': 8.0, 'defense': 7.0, 'form': 7.5}
                away_stats = {'attack': 7.5, 'defense': 6.5, 'form': 6.0}
                result_ml = analyzer_ml.predict_match(home_stats, away_stats)
            except:
                result_ml = None
            
            # Sonuçları göster
            with col1:
                st.markdown("### 📊 Basit Analiz")
                confidence_class = "confidence-high" if result_mvp['confidence'] > 70 else "confidence-medium" if result_mvp['confidence'] > 50 else "confidence-low"
                st.markdown(f"""
                <div class="prediction-card {confidence_class}">
                    <h3>Tahmin: {result_mvp['prediction']}</h3>
                    <h4>Güven: %{result_mvp['confidence']}</h4>
                    <p>Risk: {result_mvp['risk_level']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 🚀 Gelişmiş Analiz")
                confidence_class = "confidence-high" if result_api['confidence'] > 70 else "confidence-medium" if result_api['confidence'] > 50 else "confidence-low"
                st.markdown(f"""
                <div class="prediction-card {confidence_class}">
                    <h3>Tahmin: {result_api['prediction']}</h3>
                    <h4>Güven: %{result_api['confidence']}</h4>
                    <p>Value Bet: {'✅' if result_api['value_bet'] else '❌'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if result_ml:
                    st.markdown("### 🤖 ML Analizi")
                    confidence_class = "confidence-high" if result_ml['1x2_confidence'] > 70 else "confidence-medium" if result_ml['1x2_confidence'] > 50 else "confidence-low"
                    st.markdown(f"""
                    <div class="prediction-card {confidence_class}">
                        <h3>Tahmin: {result_ml['1x2_prediction']}</h3>
                        <h4>Güven: %{result_ml['1x2_confidence']}</h4>
                        <p>Gol: {result_ml['goals_prediction']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("ML modeli yüklenmedi. Önce modeli eğitin.")
            
            # Detaylı analiz grafiği
            st.markdown("---")
            st.subheader("📈 Detaylı Karşılaştırma")
            
            # Takım güçleri grafiği
            fig = go.Figure()
            
            categories = ['Atak', 'Savunma', 'Form']
            home_values = [result_mvp['home_strength']*1.2, result_mvp['home_strength']*0.9, result_mvp['home_strength']]
            away_values = [result_mvp['away_strength']*1.1, result_mvp['away_strength']*1.1, result_mvp['away_strength']*0.8]
            
            fig.add_trace(go.Scatterpolar(
                r=home_values,
                theta=categories,
                fill='toself',
                name=home_team,
                line_color='#1f77b4'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=away_values,
                theta=categories,
                fill='toself',
                name=away_team,
                line_color='#ff7f0e'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Takım Güçleri Karşılaştırması"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("❌ Lütfen farklı takımlar seçin!")

elif analysis_type == "Kupon Analizi":
    st.header("🎫 Kupon Analizi")
    
    # Kupon oluşturma
    st.subheader("Kupon Oluştur")
    
    if 'kupon_matches' not in st.session_state:
        st.session_state.kupon_matches = []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        home_team = st.selectbox("Ev Sahibi", all_teams, key="kupon_home")
    with col2:
        away_team = st.selectbox("Deplasman", all_teams, key="kupon_away")
    with col3:
        bet_type = st.selectbox("Bahis Tipi", ["1X2", "Alt/Üst 2.5"], key="kupon_bet")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Maç Ekle"):
            if home_team != away_team:
                match = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'bet_type': bet_type
                }
                st.session_state.kupon_matches.append(match)
                st.success(f"✅ {home_team} vs {away_team} eklendi!")
    
    with col2:
        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon_matches = []
            st.success("✅ Kupon temizlendi!")
    
    # Kupon görüntüleme
    if st.session_state.kupon_matches:
        st.subheader(f"📋 Kuponunuz ({len(st.session_state.kupon_matches)} maç)")
        
        for i, match in enumerate(st.session_state.kupon_matches):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{i+1}. {match['home_team']} vs {match['away_team']} - {match['bet_type']}")
            with col2:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.kupon_matches.pop(i)
                    st.rerun()
        
        # Kupon analizi
        if st.button("🔍 Kuponu Analiz Et", type="primary"):
            analyzer = KuponAnalyzer()
            result = analyzer.analyze_kupon(st.session_state.kupon_matches)
            
            # Kupon özeti
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Toplam Güven", f"%{result['kupon_confidence']}")
            with col2:
                st.metric("Maç Sayısı", result['total_matches'])
            with col3:
                risk_color = "🟢" if result['kupon_confidence'] > 25 else "🟡" if result['kupon_confidence'] > 15 else "🔴"
                st.metric("Risk", f"{risk_color}")
            
            # Öneri
            st.markdown(f"""
            <div class="prediction-card">
                <h3>Öneri: {result['recommendation']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Maç detayları
            st.subheader("📊 Maç Detayları")
            match_data = []
            for match in result['matches']:
                match_data.append({
                    'Maç': f"{match['home_team']} vs {match['away_team']}",
                    'Tahmin': match['prediction'],
                    'Güven (%)': match['confidence'],
                    'Risk': match['risk_level']
                })
            
            df = pd.DataFrame(match_data)
            st.dataframe(df, use_container_width=True)
            
            # Güven grafiği
            fig = px.bar(
                df, 
                x='Maç', 
                y='Güven (%)',
                color='Risk',
                title="Maçların Güven Seviyeleri"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Takım Karşılaştırması":
    st.header("⚔️ Takım Karşılaştırması")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("1. Takım", all_teams, key="compare1")
    with col2:
        team2 = st.selectbox("2. Takım", all_teams, key="compare2")
    
    if st.button("📊 Karşılaştır"):
        analyzer = KuponAnalyzer()
        
        team1_strength = analyzer.calculate_team_strength(team1)
        team2_strength = analyzer.calculate_team_strength(team2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🏆 {team1}")
            if team1 in analyzer.team_stats:
                stats = analyzer.team_stats[team1]
                st.metric("Atak Gücü", f"{stats['attack']}/10")
                st.metric("Savunma Gücü", f"{stats['defense']}/10")
                st.metric("Form", f"{stats['form']}/10")
                st.metric("Toplam Güç", f"{team1_strength:.1f}/10")
        
        with col2:
            st.subheader(f"🏆 {team2}")
            if team2 in analyzer.team_stats:
                stats = analyzer.team_stats[team2]
                st.metric("Atak Gücü", f"{stats['attack']}/10")
                st.metric("Savunma Gücü", f"{stats['defense']}/10")
                st.metric("Form", f"{stats['form']}/10")
                st.metric("Toplam Güç", f"{team2_strength:.1f}/10")
        
        # Karşılaştırma grafiği
        comparison_data = {
            'Takım': [team1, team2],
            'Atak': [analyzer.team_stats.get(team1, {}).get('attack', 5), 
                    analyzer.team_stats.get(team2, {}).get('attack', 5)],
            'Savunma': [analyzer.team_stats.get(team1, {}).get('defense', 5), 
                       analyzer.team_stats.get(team2, {}).get('defense', 5)],
            'Form': [analyzer.team_stats.get(team1, {}).get('form', 5), 
                    analyzer.team_stats.get(team2, {}).get('form', 5)]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        
        fig = px.bar(
            df_comparison,
            x='Takım',
            y=['Atak', 'Savunma', 'Form'],
            title="Takım İstatistikleri Karşılaştırması",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Geçmiş Performans":
    st.header("📈 Geçmiş Performans Analizi")
    
    selected_team = st.selectbox("Takım Seçin", all_teams)
    
    # Simüle edilmiş geçmiş veriler
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
    np.random.seed(42)
    
    performance_data = {
        'Tarih': dates[:20],
        'Form': np.random.uniform(3, 9, 20),
        'Atak Gücü': np.random.uniform(4, 10, 20),
        'Savunma Gücü': np.random.uniform(3, 9, 20)
    }
    
    df_performance = pd.DataFrame(performance_data)
    
    # Performans grafiği
    fig = px.line(
        df_performance,
        x='Tarih',
        y=['Form', 'Atak Gücü', 'Savunma Gücü'],
        title=f"{selected_team} - Sezonluk Performans Trendi"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # İstatistik özeti
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ortalama Form", f"{df_performance['Form'].mean():.1f}/10")
    with col2:
        st.metric("Ortalama Atak", f"{df_performance['Atak Gücü'].mean():.1f}/10")
    with col3:
        st.metric("Ortalama Savunma", f"{df_performance['Savunma Gücü'].mean():.1f}/10")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚽ Kupon Analiz Sistemi v1.0 | Geliştirici: AI Assistant</p>
    <p>⚠️ Bu sistem eğlence amaçlıdır. Yatırım tavsiyesi değildir.</p>
</div>
""", unsafe_allow_html=True)