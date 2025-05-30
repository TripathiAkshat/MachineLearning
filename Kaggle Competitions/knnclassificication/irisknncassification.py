#this is multiclass classification
from nbformat.sign import algorithms
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

data = load_iris()
# print(data.feature_names)
# print(data.target_names)
#
# ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
# ['setosa' 'versicolor' 'virginica']

X = data.data
y = data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
param_grid = {'n_neighbors': range(1, 11),'algorithm': ['auto', 'brute','ball_tree','kd_tree'],'leaf_size':[10,20,30,40,50]}
grid = GridSearchCV(KNeighborsClassifier(),param_grid, n_jobs=-1,cv=5,verbose=2)
grid.fit(X_train,y_train)
y_pred = grid.predict(X_test)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(grid.best_params_)