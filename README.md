# Churn Hunters App · Plataforma de Decisiones Predictivas (IA)

**Churn Hunters** es una solución de Inteligencia Artificial diseñada para mitigar proactivamente el abandono de clientes (*Churn*) en el canal tradicional (misceláneas y tienditas) de **Arca Continental**. A través de un modelo avanzado de Machine Learning y una interfaz analítica de última generación, transformamos datos transaccionales masivos en acciones comerciales directas en el campo.

---

## 🎯 El Reto de Negocio
Identificar con precisión matemática qué clientes están en riesgo de reducir drásticamente sus compras o abandonar la marca, permitiendo a los supervisores de ruta e ingenieros de mercado intervenir con estrategias de retención personalizadas antes de que la fuga ocurra, protegiendo un valor de mercado estimado en **$12M MXN**.

---

## 🛠️ Arquitectura de la Solución

El ecosistema de la aplicación se divide en dos capas principales:

1. **Pipeline de Inteligencia Artificial (`procesar_ia.py`):**
   * Limpieza, transformación e ingeniería de variables (*Feature Engineering*) sobre el histórico de ventas e infraestructura de frío.
   * Entrenamiento de modelos predictivos y cálculo en tiempo real de la `probabilidad_churn` por cliente.
   * Exportación de scores optimizados y matrices de importancia en `/data`.

2. **Capa de Visualización y Acción (`app.py` y `/pages`):**
   * Interfaz web multipágina de alta velocidad construida con **Streamlit**.
   * Monitoreo macro de la salud de la cartera y distribución porcentual del riesgo.
   * **Consultor Individualizado:** Fichas técnicas automatizadas que auditan el comportamiento transaccional de cada cliente y dictan un **Plan de Contención Comercial** según su nivel de criticidad.

---

## 📂 Estructura del Repositorio

```text
church-hunters-app/
├── data/                       # Almacenamiento local de datos comprimidos
│   ├── clientes_scoring_precalculado.csv  # Output del modelo de IA (Scores)
│   └── importancias.json       # Peso e impacto de las variables del modelo
├── pages/                      # Pestañas y módulos de la aplicación web
│   ├── Bases_datos.py          # Auditoría de los datasets brutos cargados
│   ├── Estrategias.py          # Panel predictivo y planes de acción comercial
│   └── Simulador.py            # Simulador de escenarios predictivos
├── env/                        # Entorno virtual de Python (Ignorado en Git)
├── .gitignore                  # Exclusión de archivos pesados y entornos
├── app.py                      # Punto de entrada principal de la plataforma
├── procesar_ia.py              # Script core del motor de Machine Learning
└── README.md                   # Documentación principal del proyecto
