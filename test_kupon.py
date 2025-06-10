# test_kupon.py
from kupon_mvp import KuponAnalyzer
from api_integration import EnhancedKuponAnalyzer
from ml_algorithm import MLKuponAnalyzer

def test_mvp():
    """Basit MVP testi"""
    print("=== MVP TEST ===")
    analyzer = KuponAnalyzer()
    
    # Test kuponu
    sample_kupon = [
        {'home_team': 'Galatasaray', 'away_team': 'Besiktas', 'bet_type': '1X2'},
        {'home_team': 'Fenerbahce', 'away_team': 'Trabzonspor', 'bet_type': '1X2'},
    ]
    
    result = analyzer.analyze_kupon(sample_kupon)
    
    print(f"Kupon Güveni: %{result['kupon_confidence']}")
    print(f"Öneri: {result['recommendation']}")
    
    for i, match in enumerate(result['matches'], 1):
        print(f"{i}. {match['home_team']} vs {match['away_team']} - {match['prediction']} (%{match['confidence']})")

def test_api_integration():
    """API entegrasyonu testi"""
    print("\n=== API INTEGRATION TEST ===")
    
    # API anahtarı olmadan test (varsayılan verilerle)
    analyzer = EnhancedKuponAnalyzer()
    
    result = analyzer.analyze_match_with_api("Galatasaray", "Fenerbahce")
    
    print(f"Maç: {result['home_team']} vs {result['away_team']}")
    print(f"Tahmin: {result['prediction']}")
    print(f"Güven: %{result['confidence']}")
    print(f"Value Bet: {'Evet' if result['value_bet'] else 'Hayır'}")

def test_ml_algorithm():
    """ML algoritması testi"""
    print("\n=== MACHINE LEARNING TEST ===")
    
    analyzer = MLKuponAnalyzer()
    
    # Modeli eğit
    print("Model eğitiliyor...")
    analyzer.train_models()
    
    # Test verisi
    home_stats = {'attack': 8.5, 'defense': 7.0, 'form': 8.0}
    away_stats = {'attack': 7.0, 'defense': 6.5, 'form': 6.0}
    
    prediction = analyzer.predict_match(home_stats, away_stats)
    
    if prediction:
        print(f"1X2 Tahmini: {prediction['1x2_prediction']} (%{prediction['1x2_confidence']})")
        print(f"Gol Tahmini: {prediction['goals_prediction']} (%{prediction['goals_confidence']})")
        print("1X2 Olasılıkları:", prediction['1x2_probabilities'])

if __name__ == "__main__":
    # Tüm testleri çalıştır
    test_mvp()
    test_api_integration()
    test_ml_algorithm()
    
    print("\n=== TESTLER TAMAMLANDI ===")