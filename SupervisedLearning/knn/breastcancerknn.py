#this was an example of single class classification
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
df = load_breast_cancer()
X = df.data
y = df.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
scaler.fit_transform(X_train)
scaler.transform(X_test)
param_grid = {'n_neighbors': list(range(1, 11)), 'weights': ['uniform', 'distance'],
              'algorithm': ['auto', 'ball_tree', 'kd_tree'],'n_jobs': [-1]}
grid = GridSearchCV(KNeighborsClassifier(), param_grid, n_jobs=-1,cv=5,verbose=2)
grid.fit(X_train, y_train)
print(grid.best_params_)
y_pred = grid.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(classification_report(y_test, y_pred))
print(df.target_names)
