from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn import tree
import matplotlib.pyplot as plt

iris = load_iris()
X = iris.data
y = iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

treeclassifier = DecisionTreeClassifier(criterion='entropy', max_depth=4, splitter='random')
treeclassifier.fit(X_train, y_train)

y_pred = treeclassifier.predict(X_test)
y_pred_proba = treeclassifier.predict_proba(X_test)

cm = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='macro')

y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
auc = roc_auc_score(y_test_bin, y_pred_proba, average='macro', multi_class='ovr')

print("Confusion Matrix:")
print(cm)
print("\nClassification Report:")
print(report)
print(f"F1 Score (Macro Average): {f1:.4f}")
print(f"AUC Score (Macro, One-vs-Rest): {auc:.4f}")

plt.figure(figsize=(15, 10))
tree.plot_tree(treeclassifier,
               feature_names=iris.feature_names,
               class_names=iris.target_names,
               filled=True)
plt.show()
