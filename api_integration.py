import requests
import json
from datetime import datetime, timedelta

class SportsDataCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Ücretsiz API'ler
        self.apis = {
            'football_data': 'https://api.football-data.org/v4/',
            'sport_api': 'https://v3.football.api-sports.io/',
            'rapid_api': 'https://api-football-v1.p.rapidapi.com/v3/'
        }
        
    def get_team_stats(self, team_name, league_id=203):  # 203 = Süper Lig
        """Takım istatistiklerini çek"""
        try:
            # Örnek API çağrısı (football-data.org)
            headers = {'X-Auth-Token': self.api_key} if self.api_key else {}
            
            # Son 10 maç verisi
            url = f"{self.apis['football_data']}teams/{team_name}/matches"
            params = {
                'limit': 10,
                'status': 'FINISHED'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self.process_team_data(data)
            else:
                # API hatası durumunda varsayılan değerler
                return self.get_default_stats(team_name)
                
        except Exception as e:
            print(f"API Hatası: {e}")
            return self.get_default_stats(team_name)
    
    def process_team_data(self, raw_data):
        """Ham veriyi işle"""
        matches = raw_data.get('matches', [])
        
        if not matches:
            return {'attack': 5.0, 'defense': 5.0, 'form': 5.0}
        
        goals_scored = []
        goals_conceded = []
        results = []
        
        for match in matches:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            
            # Hangi takım olduğunu belirle
            if home_team in match:  # Basitleştirilmiş kontrol
                goals_scored.append(home_score)
                goals_conceded.append(away_score)
                if home_score > away_score:
                    results.append('W')
                elif home_score < away_score:
                    results.append('L')
                else:
                    results.append('D')
        
        # İstatistikleri hesapla
        attack_rating = sum(goals_scored) / len(goals_scored) * 2 if goals_scored else 5.0
        defense_rating = 10 - (sum(goals_conceded) / len(goals_conceded) * 2) if goals_conceded else 5.0
        
        # Form hesapla (son 5 maç)
        recent_results = results[-5:]
        wins = recent_results.count('W')
        draws = recent_results.count('D')
        form_rating = (wins * 3 + draws * 1) / (len(recent_results) * 3) * 10
        
        return {
            'attack': min(10, max(1, attack_rating)),
            'defense': min(10, max(1, defense_rating)),
            'form': min(10, max(1, form_rating))
        }
    
    def get_default_stats(self, team_name):
        """Varsayılan takım istatistikleri"""
        # Türk takımları için temel değerler
        default_stats = {
            'Galatasaray': {'attack': 8.5, 'defense': 7.0, 'form': 8.0},
            'Fenerbahçe': {'attack': 8.0, 'defense': 7.5, 'form': 7.5},
            'Beşiktaş': {'attack': 7.5, 'defense': 6.5, 'form': 6.0},
            'Trabzonspor': {'attack': 7.0, 'defense': 6.0, 'form': 6.5},
            'Başakşehir': {'attack': 6.5, 'defense': 6.5, 'form': 6.0},
        }
        
        return default_stats.get(team_name, {'attack': 5.0, 'defense': 5.0, 'form': 5.0})
    
    def get_head_to_head(self, team1, team2):
        """İki takım arasındaki geçmiş karşılaşmalar"""
        # Bu fonksiyon API'den son karşılaşmaları çeker
        # Şimdilik basit bir örnek
        return {
            'total_matches': 10,
            'team1_wins': 4,
            'team2_wins': 3,
            'draws': 3,
            'avg_goals': 2.3
        }
    
    def get_current_odds(self, match_info):
        """Güncel bahis oranları"""
        # Bahis sitelerinden oran çekme (dikkat: yasal durumu kontrol edin)
        # Örnek veri
        return {
            '1': 2.1,
            'X': 3.2,
            '2': 4.5,
            'over_2_5': 1.8,
            'under_2_5': 2.0
        }

class EnhancedKuponAnalyzer:
    def __init__(self, api_key=None):
        self.data_collector = SportsDataCollector(api_key)
        
    def analyze_match_with_api(self, home_team, away_team, bet_type="1X2"):
        """API verisi ile gelişmiş maç analizi"""
        
        # Takım verilerini API'den çek
        home_stats = self.data_collector.get_team_stats(home_team)
        away_stats = self.data_collector.get_team_stats(away_team)
        
        # Geçmiş karşılaşmalar
        h2h = self.data_collector.get_head_to_head(home_team, away_team)
        
        # Bahis oranları
        odds = self.data_collector.get_current_odds({'home': home_team, 'away': away_team})
        
        # Gelişmiş analiz
        home_strength = (home_stats['attack'] + home_stats['defense'] + home_stats['form']) / 3
        away_strength = (away_stats['attack'] + away_stats['defense'] + away_stats['form']) / 3
        
        # Ev sahibi avantajı ekle
        home_strength *= 1.2
        
        # Head-to-head faktörü
        h2h_factor = 1.0
        if h2h['team1_wins'] > h2h['team2_wins']:
            h2h_factor = 1.1
        elif h2h['team2_wins'] > h2h['team1_wins']:
            h2h_factor = 0.9
        
        home_strength *= h2h_factor
        
        # Oran analizi (value betting)
        implied_prob_home = 1 / odds['1']
        calculated_prob_home = home_strength / (home_strength + away_strength)
        
        value = calculated_prob_home - implied_prob_home
        
        # Tahmin
        strength_diff = home_strength - away_strength
        
        if bet_type == "1X2":
            if strength_diff > 1.0 and value > 0.1:
                prediction = "1"
                confidence = min(85, 65 + (strength_diff * 8))
            elif strength_diff < -1.0 and value < -0.1:
                prediction = "2"
                confidence = min(85, 65 + (abs(strength_diff) * 8))
            else:
                prediction = "X"
                confidence = 45 + (5 - abs(strength_diff))
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction': prediction,
            'confidence': round(confidence, 1),
            'value_bet': value > 0.05,
            'odds_analysis': {
                'recommended_odd': odds.get(prediction.lower(), odds.get(prediction, 0)),
                'value_score': round(value, 3)
            },
            'factors': {
                'home_strength': round(home_strength, 2),
                'away_strength': round(away_strength, 2),
                'h2h_advantage': h2h_factor,
                'form_home': home_stats['form'],
                'form_away': away_stats['form']
            }
        }

# Test
if __name__ == "__main__":
    # API anahtarınızı buraya ekleyin
    analyzer = EnhancedKuponAnalyzer(api_key="YOUR_API_KEY_HERE")
    
    result = analyzer.analyze_match_with_api("Galatasaray", "Fenerbahçe")
    
    print("=== GELİŞMİŞ ANALİZ ===")
    print(f"Maç: {result['home_team']} vs {result['away_team']}")
    print(f"Tahmin: {result['prediction']}")
    print(f"Güven: %{result['confidence']}")
    print(f"Value Bet: {'Evet' if result['value_bet'] else 'Hayır'}")
    print(f"Önerilen Oran: {result['odds_analysis']['recommended_odd']}")