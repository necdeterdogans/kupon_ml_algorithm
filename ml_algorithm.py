import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
from datetime import datetime, timedelta

class MLKuponAnalyzer:
    def __init__(self):
        self.model_1x2 = None
        self.model_goals = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def create_features(self, home_team_stats, away_team_stats, additional_data=None):
        """Makine öğrenmesi için özellik vektörü oluştur"""
        features = []
        
        # Temel takım istatistikleri
        features.extend([
            home_team_stats['attack'],
            home_team_stats['defense'], 
            home_team_stats['form'],
            away_team_stats['attack'],
            away_team_stats['defense'],
            away_team_stats['form']
        ])
        
        # Türetilmiş özellikler
        attack_diff = home_team_stats['attack'] - away_team_stats['attack']
        defense_diff = home_team_stats['defense'] - away_team_stats['defense']
        form_diff = home_team_stats['form'] - away_team_stats['form']
        
        features.extend([attack_diff, defense_diff, form_diff])
        
        # Ek veriler varsa
        if additional_data:
            features.extend([
                additional_data.get('h2h_home_wins', 0) / max(additional_data.get('total_h2h', 1), 1),
                additional_data.get('h2h_away_wins', 0) / max(additional_data.get('total_h2h', 1), 1),
                additional_data.get('avg_goals_h2h', 2.5),
                additional_data.get('home_advantage', 1.2),
                additional_data.get('weather_factor', 1.0),
                additional_data.get('referee_factor', 1.0)
            ])
        else:
            features.extend([0.4, 0.3, 2.5, 1.2, 1.0, 1.0])
        
        return np.array(features).reshape(1, -1)
    
    def generate_training_data(self, num_samples=1000):
        """Eğitim verisi oluştur (gerçek projede tarihsel veriler kullanılır)"""
        np.random.seed(42)
        
        training_data = []
        labels_1x2 = []
        labels_goals = []
        
        for _ in range(num_samples):
            # Rastgele takım istatistikleri
            home_attack = np.random.uniform(3, 10)
            home_defense = np.random.uniform(3, 10)
            home_form = np.random.uniform(3, 10)
            
            away_attack = np.random.uniform(3, 10)
            away_defense = np.random.uniform(3, 10)
            away_form = np.random.uniform(3, 10)
            
            # Ek faktörler
            h2h_home = np.random.uniform(0, 1)
            h2h_away = np.random.uniform(0, 1-h2h_home)
            avg_goals = np.random.uniform(1.5, 4.0)
            home_advantage = np.random.uniform(1.0, 1.5)
            
            features = [
                home_attack, home_defense, home_form,
                away_attack, away_defense, away_form,
                home_attack - away_attack,
                home_defense - away_defense,
                home_form - away_form,
                h2h_home, h2h_away, avg_goals, home_advantage, 1.0, 1.0
            ]
            
            # Basit hedef değişken hesaplama (gerçekte maç sonuçları olur)
            home_strength = (home_attack + home_defense + home_form) * home_advantage
            away_strength = away_attack + away_defense + away_form
            
            strength_diff = home_strength - away_strength
            
            # 1X2 etiketi
            if strength_diff > 3:
                label_1x2 = 0  # Home win
            elif strength_diff < -3:
                label_1x2 = 2  # Away win
            else:
                label_1x2 = 1  # Draw
            
            # Gol etiketi (2.5 üst/alt)
            expected_goals = (home_attack + away_attack) / 4 + avg_goals / 3
            label_goals = 1 if expected_goals > 2.5 else 0
            
            training_data.append(features)
            labels_1x2.append(label_1x2)
            labels_goals.append(label_goals)
        
        return np.array(training_data), np.array(labels_1x2), np.array(labels_goals)
    
    def train_models(self):
        """Modelleri eğit"""
        print("Eğitim verisi oluşturuluyor...")
        X, y_1x2, y_goals = self.generate_training_data(2000)
        
        # Veriyi böl
        X_train, X_test, y_1x2_train, y_1x2_test = train_test_split(X, y_1x2, test_size=0.2, random_state=42)
        _, _, y_goals_train, y_goals_test = train_test_split(X, y_goals, test_size=0.2, random_state=42)
        
        # Veriyi standartlaştır
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("1X2 modeli eğitiliyor...")
        # 1X2 modeli
        self.model_1x2 = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.model_1x2.fit(X_train_scaled, y_1x2_train)
        
        print("Gol modeli eğitiliyor...")
        # Gol modeli
        self.model_goals = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.model_goals.fit(X_train_scaled, y_goals_train)
        
        # Test et
        y_1x2_pred = self.model_1x2.predict(X_test_scaled)
        y_goals_pred = self.model_goals.predict(X_test_scaled)
        
        print(f"1X2 Model Doğruluğu: {accuracy_score(y_1x2_test, y_1x2_pred):.2f}")
        print(f"Gol Model Doğruluğu: {accuracy_score(y_goals_test, y_goals_pred):.2f}")
        
        self.is_trained = True
        
        # Modelleri kaydet
        joblib.dump(self.model_1x2, 'model_1x2.pkl')
        joblib.dump(self.model_goals, 'model_goals.pkl')
        joblib.dump(self.scaler, 'scaler.pkl')
        
        print("Modeller kaydedildi!")
    
    def load_models(self):
        """Kaydedilmiş modelleri yükle"""
        try:
            self.model_1x2 = joblib.load('model_1x2.pkl')
            self.model_goals = joblib.load('model_goals.pkl')
            self.scaler = joblib.load('scaler.pkl')
            self.is_trained = True
            print("Modeller yüklendi!")
        except FileNotFoundError:
            print("Model dosyaları bulunamadı. Önce train_models() çalıştırın.")
    
    def predict_match(self, home_team_stats, away_team_stats, additional_data=None):
        """ML ile maç tahmini"""
        if not self.is_trained:
            print("Model eğitilmemiş! Önce train_models() veya load_models() çalıştırın.")
            return None
        
        # Özellik vektörü oluştur
        features = self.create_features(home_team_stats, away_team_stats, additional_data)
        features_scaled = self.scaler.transform(features)
        
        # 1X2 tahmini
        prob_1x2 = self.model_1x2.predict_proba(features_scaled)[0]
        pred_1x2 = self.model_1x2.predict(features_scaled)[0]
        
        # Gol tahmini
        prob_goals = self.model_goals.predict_proba(features_scaled)[0]
        pred_goals = self.model_goals.predict(features_scaled)[0]
        
        # Sonuçları yorumla
        labels_1x2 = ['1', 'X', '2']
        labels_goals = ['Alt 2.5', 'Üst 2.5']
        
        return {
            '1x2_prediction': labels_1x2[pred_1x2],
            '1x2_confidence': round(max(prob_1x2) * 100, 1),
            '1x2_probabilities': {
                '1': round(prob_1x2[0] * 100, 1),
                'X': round(prob_1x2[1] * 100, 1),
                '2': round(prob_1x2[2] * 100, 1)
            },
            'goals_prediction': labels_goals[pred_goals],
            'goals_confidence': round(max(prob_goals) * 100, 1),
            'goals_probabilities': {
                'Alt 2.5': round(prob_goals[0] * 100, 1),
                'Üst 2.5': round(prob_goals[1] * 100, 1)
            }
        }
    
    def analyze_kupon_ml(self, matches_data):
        """Tüm kuponu ML ile analiz et"""
        results = []
        total_confidence = 1.0
        
        for match in matches_data:
            prediction = self.predict_match(
                match['home_stats'],
                match['away_stats'],
                match.get('additional_data')
            )
            
            if prediction:
                results.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'prediction': prediction
                })
                
                # En yüksek güven oranını al
                best_confidence = max(
                    prediction['1x2_confidence'],
                    prediction['goals_confidence']
                ) / 100
                
                total_confidence *= best_confidence
        
        kupon_confidence = total_confidence * 100
        
        return {
            'matches': results,
            'kupon_confidence': round(kupon_confidence, 2),
            'recommendation': self.get_ml_recommendation(kupon_confidence),
            'risk_analysis': self.analyze_risk(results)
        }
    
    def get_ml_recommendation(self, confidence):
        """ML bazlı öneri"""
        if confidence >= 30:
            return "Güçlü Kupon - Oynabilir"
        elif confidence >= 20:
            return "Orta Güven - Dikkatli Oyna"
        elif confidence >= 10:
            return "Düşük Güven - Küçük Miktarla"
        else:
            return "Çok Riskli - Oynama"
    
    def analyze_risk(self, results):
        """Risk analizi"""
        high_confidence_count = 0
        total_matches = len(results)
        
        for match in results:
            pred = match['prediction']
            max_conf = max(pred['1x2_confidence'], pred['goals_confidence'])
            if max_conf >= 70:
                high_confidence_count += 1
        
        risk_score = (high_confidence_count / total_matches) * 100 if total_matches > 0 else 0
        
        if risk_score >= 60:
            return "Düşük Risk"
        elif risk_score >= 30:
            return "Orta Risk"
        else:
            return "Yüksek Risk"
        # Test kodu - dosyanın en sonuna ekleyin
if __name__ == "__main__":
    print("ML Kupon Analyzer sınıfı hazır!")
    print("Test için: python test_kupon.py çalıştırın")