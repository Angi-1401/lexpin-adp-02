### 1. Perfil Calórico y Distribución de Macronutrientes (% de Calorías)

Este análisis permite evaluar qué porcentaje de la energía total (calorías) proviene de cada macronutriente (proteínas, carbohidratos y grasas), identificando si una bebida se alinea con un perfil hiperglucémico (alto en carbohidratos/azúcares) o alto en grasas.

* **Columnas necesarias:**
* *Disponibles:* `Calories`, `Total_Fat_(g)`, `Total_Carbohydrates_(g)`, `Protein_(g)`
* *Nuevas columnas a crear:*
* `Cal_Fat` = `Total_Fat_(g)` $\times$ 9
* `Cal_Carb` = `Total_Carbohydrates_(g)` $\times$ 4
* `Cal_Protein` = `Protein_(g)` $\times$ 4
* `Pct_Cal_Fat` = (`Cal_Fat` / `Calories`) $\times$ 100
* `Pct_Cal_Carb` = (`Cal_Carb` / `Calories`) $\times$ 100
* `Pct_Cal_Protein` = (`Cal_Protein` / `Calories`) $\times$ 100
* **Método de cálculo:** Se utilizan los factores de Atwater estándar (9 kcal/g para grasas, 4 kcal/g para carbohidratos y proteínas) para convertir gramos a calorías y calcular la proporción porcentual respecto a las `Calories` totales.
* **Figura de Plotly ideal:** **Gráfico de dispersión ternario (`go.Scatterternum`)** o un **gráfico de barras apiladas al 100% (`px.bar` con `barmode='relative'` y normalizado)** para ver la composición porcentual de macronutrientes por categoría de bebida.

---

### 2. Densidad de Azúcares Libres vs. Carga Calórica Total

Permite identificar qué bebidas aportan una cantidad excesiva de azúcares simples en relación con su volumen calórico total, lo cual es crítico para la prevención de resistencia a la insulina y obesidad.

* **Columnas necesarias:**
* *Disponibles:* `Sugars_(g)`, `Calories`, `Beverage_Category`, `Beverage`
* *Nuevas columnas a crear:*
* `Cal_From_Sugar` = `Sugars_(g)` $\times$ 4
* `Sugar_Cal_Ratio` = (`Cal_From_Sugar` / `Calories`) $\times$ 100 (Porcentaje de calorías provenientes exclusivamente del azúcar).
* **Método de cálculo:** Multiplicar los gramos de azúcar por 4 kcal/g y dividir entre las calorías totales para obtener la contribución porcentual del azúcar libre a la energía de la bebida.
* **Figura de Plotly ideal:** **Gráfico de dispersión (`px.scatter`)** con `Sugars_(g)` en el eje X, `Calories` en el eje Y, coloreado por `Beverage_Category` y con una línea de referencia que marque el límite recomendado del 10% o 25% de calorías de azúcares libres.

---

### 3. Impacto de la Preparación (`Beverage_Prep`) en la Modificación Nutricional

Cuantifica cómo cambia el perfil nutricional de una misma bebida base (ej. un Caffè Latte) al modificar el tipo de leche o el tamaño de la preparación (entera, descremada, soja, grande, venti, etc.).

* **Columnas necesarias:**
* *Disponibles:* `Beverage`, `Beverage_Prep`, `Calories`, `Total_Fat_(g)`, `Sugars_(g)`
* *Nuevas columnas a crear:*
* `Delta_Calories` (Diferencia porcentual o absoluta de calorías respecto a la preparación base o de referencia, calculada mediante agrupación por `Beverage`).
* **Método de cálculo:** Agrupación por el nombre de la bebida (`Beverage`) y comparación estadística de las medias de calorías y grasas entre los diferentes tipos de `Beverage_Prep`.
* **Figura de Plotly ideal:** **Diagrama de caja agrupado (`px.box`)** o **gráfico de barras agrupadas (`px.bar`)** comparando las calorías y grasas de distintas preparaciones para una selección de bebidas populares.

---

### 4. Relación Nutrimental: Densidad de Calcio y Hierro vs. Densidad Energética

Evalúa si las bebidas con mayor contenido calórico ofrecen un beneficio nutricional proporcional en términos de micronutrientes esenciales (`Calcium_(% DV)` e `Iron_(% DV)`) o si solo aportan "calorías vacías".

* **Columnas necesarias:**
* *Disponibles:* `Calcium_(% DV)`, `Iron_(% DV)`, `Calories`, `Beverage_Category`
* *Nuevas columnas a crear:*
* `Nutrient_Density_Index` = (`Calcium_(% DV)` + `Iron_(% DV)`) / (`Calories` / 100) (Aporte de minerales por cada 100 kcal).
* **Método de cálculo:** Sumar los porcentajes de valor diario de calcio y hierro y normalizarlos por cada 100 kilocalorías de la bebida.
* **Figura de Plotly ideal:** **Gráfico de burbujas (`px.scatter`)** donde el eje X sean las `Calories`, el eje Y el índice de micronutrientes (`Nutrient_Density_Index`), y el tamaño de la burbuja represente el contenido de `Protein_(g)`.

---

### 5. Distribución y Exposición a la Cafeína por Categoría de Bebida

Analiza la variabilidad del estimulante principal en función de la categoría de la bebida, lo cual es relevante desde el punto de vista clínico para pacientes con sensibilidad a la cafeína, hipertensión o ansiedad.

* **Columnas necesarias:**
* *Disponibles:* `Caffeine_(mg)`, `Beverage_Category`
* *Nuevas columnas a crear:* Ninguna estrictamente necesaria (se pueden usar umbrales categóricos derivados como `High_Caffeine` si se desea clasificar $>150$ mg).
* **Método de cálculo:** Cálculo de la media, mediana, cuartiles y valores máximos/mínimos de `Caffeine_(mg)` agrupados por `Beverage_Category`.
* **Figura de Plotly ideal:** **Gráfico de violín (`px.violin`)** combinado con puntos de dispersión (`box=True`, `points="all"`) para mostrar la densidad y dispersión de los niveles de cafeína en cada categoría.

---
