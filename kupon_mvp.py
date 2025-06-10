import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class KuponAnalyzer:
    def __init__(self):
        # Basit takım verileri (gerçek API'den gelecek)
        self.team_stats = {
            'Galatasaray': {'attack': 8.5, 'defense': 7.0, 'form': 8.0, 'home_advantage': 1.2},
            'Fenerbahce': {'attack': 8.0, 'defense': 7.5, 'form': 7.5, 'home_advantage': 1.1},
            'Besiktas': {'attack': 7.5, 'defense': 6.5, 'form': 6.0, 'home_advantage': 1.0},
            'Trabzonspor': {'attack': 7.0, 'defense': 6.0, 'form': 6.5, 'home_advantage': 1.1}
        }
    
    def calculate_team_strength(self, team_name, is_home=False):
        """Takım gücünü hesapla"""
        if team_name not in self.team_stats:
            return 5.0  # Varsayılan değer
        
        stats = self.team_stats[team_name]
        strength = (stats['attack'] + stats['defense'] + stats['form']) / 3
        
        if is_home:
            strength *= stats['home_advantage']
        
        return strength
    
    def analyze_match(self, home_team, away_team, bet_type="1X2"):
        """Maç analizi yap"""
        home_strength = self.calculate_team_strength(home_team, is_home=True)
        away_strength = self.calculate_team_strength(away_team, is_home=False)
        
        # Basit tahmin algoritması
        strength_diff = home_strength - away_strength
        
        # 1X2 analizi
        if bet_type == "1X2":
            if strength_diff > 1.5:
                prediction = "1"  # Ev sahibi kazanır
                confidence = min(80, 60 + (strength_diff * 10))
            elif strength_diff < -1.5:
                prediction = "2"  # Deplasman kazanır
                confidence = min(80, 60 + (abs(strength_diff) * 10))
            else:
                prediction = "X"  # Beraberlik
                confidence = 50 + (10 - abs(strength_diff) * 5)
        
        # Alt/Üst 2.5 gol analizi
        elif bet_type == "O/U2.5":
            total_attack = (self.team_stats.get(home_team, {}).get('attack', 5) + 
                          self.team_stats.get(away_team, {}).get('attack', 5)) / 2
            if total_attack > 7.5:
                prediction = "Üst 2.5"
                confidence = min(75, 50 + (total_attack - 7.5) * 10)
            else:
                prediction = "Alt 2.5"
                confidence = min(75, 50 + (7.5 - total_attack) * 10)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction': prediction,
            'confidence': round(confidence, 1),
            'home_strength': round(home_strength, 2),
            'away_strength': round(away_strength, 2),
            'risk_level': self.calculate_risk(confidence)
        }
    
    def calculate_risk(self, confidence):
        """Risk seviyesi hesapla"""
        if confidence >= 70:
            return "Düşük"
        elif confidence >= 55:
            return "Orta"
        else:
            return "Yüksek"
    
    def analyze_kupon(self, matches):
        """Tüm kuponu analiz et"""
        kupon_analizi = []
        total_confidence = 1.0
        
        for match in matches:
            analiz = self.analyze_match(
                match['home_team'], 
                match['away_team'], 
                match.get('bet_type', '1X2')
            )
            kupon_analizi.append(analiz)
            total_confidence *= (analiz['confidence'] / 100)
        
        kupon_confidence = total_confidence * 100
        
        return {
            'matches': kupon_analizi,
            'kupon_confidence': round(kupon_confidence, 2),
            'recommendation': self.get_recommendation(kupon_confidence),
            'total_matches': len(matches)
        }
    
    def get_recommendation(self, confidence):
        """Kupon önerisi ver"""
        if confidence >= 25:
            return "Oynabilir - İyi görünüyor"
        elif confidence >= 15:
            return "Dikkatli oyna - Orta risk"
        else:
            return "Oynama - Yüksek risk"

# Test için örnek kullanım
if __name__ == "__main__":
    analyzer = KuponAnalyzer()
    
    # Örnek kupon
    sample_kupon = [
        {'home_team': 'Galatasaray', 'away_team': 'Besiktas', 'bet_type': '1X2'},
        {'home_team': 'Fenerbahce', 'away_team': 'Trabzonspor', 'bet_type': '1X2'},
        {'home_team': 'Galatasaray', 'away_team': 'Fenerbahce', 'bet_type': 'O/U2.5'}
    ]
    
    # Analiz yap
    result = analyzer.analyze_kupon(sample_kupon)
    
    print("=== KUPON ANALİZİ ===")
    print(f"Toplam Güven: %{result['kupon_confidence']}")
    print(f"Öneri: {result['recommendation']}")
    print("\n=== MAÇLAR ===")
    
    for i, match in enumerate(result['matches'], 1):
        print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
        print(f"   Tahmin: {match['prediction']}")
        print(f"   Güven: %{match['confidence']}")
        print(f"   Risk: {match['risk_level']}")