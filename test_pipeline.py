import numpy as np
from ucimlrepo import fetch_ucirepo
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def test_data_ingestion():
    dataset = fetch_ucirepo(id=291)
    assert dataset is not None, "blad pobierania danych z uci repo"
    assert dataset.data.features.shape[0] == 1503, "niepoprawna liczba rekordow"

def test_feature_engineering():
    dataset = fetch_ucirepo(id=291)
    df = dataset.data.features.copy()
    df.columns = ['Frequency', 'Angle_of_attack', 'Chord_length', 'Free_stream_velocity', 'Suction_side_displacement_thickness']
    
    nu = 1.5e-5
    st = (df['Frequency'] * df['Suction_side_displacement_thickness']) / df['Free_stream_velocity']
    re = (df['Free_stream_velocity'] * df['Chord_length']) / nu
    
    assert not st.isnull().any(), "liczba strouhala zawiera wartosci nan"
    assert not np.isinf(st).any(), "liczba strouhala zawiera nieskonczonosc"
    assert (st > 0).all(), "liczba strouhala musi byc dodatnia"
    assert (re > 0).all(), "liczba reynoldsa musi byc dodatnia"

def test_surrogate_model_convergence():
    dataset = fetch_ucirepo(id=291)
    X = dataset.data.features.copy()
    y = dataset.data.targets.values.ravel()
    
    # obliczenie cechy strouhala
    X['Strouhal'] = (X.iloc[:, 0] * X.iloc[:, 4]) / X.iloc[:, 3]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=30, random_state=42)
    model.fit(X_train, y_train)
    
    r2 = r2_score(y_test, model.predict(X_test))
    assert r2 >= 0.85, f"model osiagnal zbyt niski r2: {r2:.4f}"

if __name__ == "__main__":
    print("uruchamianie testow integralnosci pipeline'u...")
    test_data_ingestion()
    test_feature_engineering()
    test_surrogate_model_convergence()
    print("wszystkie testy zakonczone sukcesem.")