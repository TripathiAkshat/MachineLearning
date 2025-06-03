from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV


iris = load_iris()
X = iris.data
y = iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
param_grid = {'criterion':['gini','entropy','log_loss'],
              }
grid = GridSearchCV(RandomForestClassifier(), param_grid=param_grid, cv=5,n_jobs=-1,verbose=3)
scaler = StandardScaler()
scaler.fit_transform(X_train)
scaler.transform(X_test)
grid.fit(X_train, y_train)
y_pred = grid.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(classification_report(y_test, y_pred))
print(grid.best_params_)

