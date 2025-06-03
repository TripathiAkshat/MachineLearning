from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_diabetes
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

diabetes = load_diabetes()
X = diabetes.data
y = diabetes.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
scaler.fit_transform(X_train)
scaler.transform(X_test)

param_grid = {
    'max_depth': range(1, 5),
    'criterion': ['squared_error', 'friedman_mse', 'absolute_error'],
}

grid = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5, verbose=2, n_jobs=-1)
grid.fit(X_train, y_train)

y_pred = grid.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))
