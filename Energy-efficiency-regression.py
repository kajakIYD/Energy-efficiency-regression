#!/usr/bin/env python
# coding: utf-8

# # Predykcja wydajności energetycznej
# 
# Dokonuję analizy energetycznej wykorzystując 12 różnych kształtów budynków symulowanych w programie Ecotect [1]. Budynki różnią się między innymi obszarem oszklenia, rozkładem powierzchni oszklenia i orientacją. 
# Zestaw danych obejmuje 768 próbek i 8 funkcji, których celem jest przewidzenie dwóch odpowiedzi o wartościach rzeczywistych.
# Informacje o cechach/feature'ach w zbiorze:
# Zestaw danych zawiera osiem atrybutów (lub funkcji oznaczonych jako X1 ... X8) oraz wartości wyjściowej (oznaczone jako y1).
# Celem jest wykorzystanie ośmiu cech do wyznaczenia wartości wyjściowej.
# <br>
# Konkretnie:
# <br>
# - X1 Względna zwartość
# - X2 Powierzchnia
# - X3 Obszar ściany
# - X4 Powierzchnia dachu
# - X5 Wysokość całkowita
# - X6 Orientacja
# - X7 Obszar szklenia
# - X8 Rozkład powierzchni oszklenia
# - y1 Obciążenie grzewcze
# 
# <br>
# [1] - A. Tsanas, A. Xifara: 'Accurate quantitative estimation of energy performance of residential buildings using statistical machine learning tools', Energy and Buildings, Vol. 49, pp. 560-567, 2012
# <br>
# Źródło: https://archive.ics.uci.edu/ml/datasets/Energy+efficiency

# # Kod programu

# In[54]:


import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline


# In[55]:


df = pd.read_excel("ENB2012_data.xlsx")
df = df.iloc[:, :-1]  # exclude output value Y2
df


# ## Histogramy

# In[56]:


ax = plt.figure(figsize=(12,12)).gca()
df.hist(ax=ax)


# ## Korelacje pomiędzy cechami a wartością wyjściową (współczynnik korelacji Pearsona)

# In[57]:


df_corr_y1 = df.corr()['Y1'][:-1]
#set fig size
fig, ax = plt.subplots(figsize=(10,10))
#plot matrix
sns.heatmap(df_corr_y1.to_frame(),annot=True, annot_kws={'size':24})
plt.show()


# ## Przygotowanie zbioru treningowego i testowego

# In[58]:


output = "Y1"
features = list(df.columns)
features.remove(output)

X = df[features].to_numpy()
y = df[output].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)


# ### Regresja liniowa
# $y = b + z_1x_1 + z_2x_2 + ... $

# In[74]:


reg = LinearRegression().fit(X_train, y_train)
print("Współczynnik dopasowania R^2 do zbioru testowego:", reg.score(X_test, y_test))
print("Współczynniki regresji:", reg.coef_)
print("Bias:", reg.intercept_)

y_to_plot = reg.predict(X)
sns.scatterplot(
    x=df.index,
    y=y_to_plot,
    label="Predicted value"
)
sns.scatterplot(
    x=df.index,
    y=y,
    label="True value"
)
plt.title("Linear regression - results comparison")
plt.legend()
plt.show()

sns.scatterplot(
    x=df.index,
    y=y_to_plot - y,
    label="Errors for each instance"
)
plt.title("Linear regression - errors values")
plt.legend()
plt.show()


# ### Regresja wielomianowa - spośród wszystkich daje najlepszy wynik
# $y = b + z_1x_1 + z_2x_2 + z_3x_1^2 + z_4x_2^2 + z_5x_1x_2 + ... $

# In[75]:


model = Pipeline([('poly', PolynomialFeatures(degree=2)),
                  ('linear', LinearRegression())])

model = model.fit(X_train, y_train)
print("Współczynnika dopasowania R^2 do zbioru testowego", model.score(X_test, y_test))
print("Współczynniki regresji:", model.named_steps['linear'].coef_)
print("Bias:", model.named_steps['linear'].intercept_)

y_to_plot = model.predict(X)
sns.scatterplot(
    x=df.index,
    y=y_to_plot,
    label="Predicted value"
)
sns.scatterplot(
    x=df.index,
    y=y,
    label="True value"
)
plt.title("Polynomial regression - results comparison")
plt.legend()
plt.show()

sns.scatterplot(
    x=df.index,
    y=y_to_plot - y,
    label="Errors for each instance"
)
plt.title("Linear regression - errors values")
plt.legend()
plt.show()


# ### Regresja metodą stochastycznego spadku gradientowego

# In[76]:


model = Pipeline([
    ('scale', StandardScaler()),
    ('regression', SGDRegressor(
        penalty='elasticnet', alpha=0.01, l1_ratio=0.25, tol=1e-4)  # SGD regression with elasticnet regularization penalty
    )
])

model = model.fit(X_train, y_train)
print("Współczynnika dopasowania do zbioru testowego R^2", model.score(X_test, y_test))
print("Współczynniki regresji:", model.named_steps['regression'].coef_)
print("Bias:", model.named_steps['regression'].intercept_)

y_to_plot = model.predict(X)
sns.scatterplot(
    x=df.index,
    y=y_to_plot,
    label="Predicted value"
)
sns.scatterplot(
    x=df.index,
    y=y,
    label="True value"
)
plt.title("SGD regression - results comparison")
plt.legend()
plt.show()

sns.scatterplot(
    x=df.index,
    y=y_to_plot - y,
    label="Errors for each instance"
)
plt.title("SGD regression - errors values")
plt.legend()
plt.show()

