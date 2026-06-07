import os
import pandas as pd
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, classification_report,
    confusion_matrix, roc_curve
)

def ejecutar_entrenamiento_ia():
    print(" Cargando datos desde la carpeta local...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_train    = os.path.join(base_dir, "data", "sales_churn_train.csv")
    path_clientes = os.path.join(base_dir, "data", "Clientes.csv")
    path_coolers  = os.path.join(base_dir, "data", "Coolers.csv")

    if not (os.path.exists(path_train) and os.path.exists(path_clientes) and os.path.exists(path_coolers)):
        print("❌ Error: No se encontraron los archivos CSV en la carpeta data/")
        return

    train    = pd.read_csv(path_train)
    clientes = pd.read_csv(path_clientes)
    coolers  = pd.read_csv(path_coolers)

    print("🧠 Procesando Ingeniería de Features...")

    # ── Agregación principal por cliente ──
    cust = train.groupby("customer_id").agg(
        meses_activo        = ("calmonth",          "count"),
        total_transacciones = ("num_transacciones",  "sum"),
        avg_transacciones   = ("num_transacciones",  "mean"),
        avg_boxes           = ("uni_boxes_sold_m",   "mean"),
        total_boxes         = ("uni_boxes_sold_m",   "sum"),
        churned             = ("target",             "max"),
    ).reset_index()

    # ── Tendencia: ratio de actividad reciente vs. temprana ──
    train_sorted = train.sort_values(["customer_id", "calmonth"])
    train_sorted['rank_asc']  = train_sorted.groupby('customer_id').cumcount()
    train_sorted['rank_desc'] = train_sorted.groupby('customer_id').cumcount(ascending=False)

    early_mean = train_sorted[train_sorted['rank_asc']  < 3].groupby('customer_id')['num_transacciones'].mean()
    late_mean  = train_sorted[train_sorted['rank_desc'] < 3].groupby('customer_id')['num_transacciones'].mean()

    trend = pd.DataFrame(index=cust['customer_id'])
    trend['early'] = early_mean
    trend['late']  = late_mean
    trend['trend_ratio'] = (trend['late'] / trend['early']).fillna(1.0)
    trend.loc[trend['early'] == 0, 'trend_ratio'] = 1.0
    cust = cust.merge(trend['trend_ratio'].reset_index(), on="customer_id", how="left")

    # ── Coolers (CORREGIDO: Garantiza infraestructura de frío para todos) ──
    cooler_flag = coolers.groupby("customer_id")["num_coolers"].mean().reset_index()
    cooler_flag.columns = ["customer_id", "avg_coolers"]
    
    # Cruzamos los datos de coolers
    cust = cust.merge(cooler_flag[["customer_id", "avg_coolers"]], on="customer_id", how="left")
    
    # Si por error de ID no cruzó con la tabla base, le asignamos un promedio de 1 cooler por tienda
    cust["avg_coolers"] = cust["avg_coolers"].fillna(1)
    
    # Como por regla de negocio todas las tiendas de la muestra tienen activo de frío, forzamos la bandera a 1
    cust["tiene_cooler"] = 1

    # ── Merge con clientes ──
    cust = cust.merge(clientes, on="customer_id", how="left")

    # ── Detección robusta de columna de territorio ──
    columna_territorio = None
    for col in cust.columns:
        if 'territor' in col.lower() or 'zona' in col.lower():
            columna_territorio = col
            break

    if columna_territorio:
        print(f"📍 Columna de territorio detectada como: '{columna_territorio}'")
        cust['territorio_encoded'] = cust[columna_territorio].astype('category').cat.codes
        if 'territory_id' not in cust.columns:
            cust['territory_id'] = cust[columna_territorio]
    else:
        print("⚠️ No se encontró columna de territorio. Asignando valores genéricos...")
        cust['territorio_encoded'] = 0
        cust['territory_id'] = "Zona General"

    # ── Preparar features y target ──
    features_ml = [
        'meses_activo', 'total_transacciones', 'avg_transacciones',
        'avg_boxes', 'total_boxes', 'trend_ratio',
        'tiene_cooler', 'avg_coolers', 'territorio_encoded'
    ]
    X = cust[features_ml].fillna(0)
    y = cust['churned'].fillna(0).astype(int)

    # ────────────────────────────────────────────────────────────
    # 🛡️ CORRECCIÓN: train/test split para métricas honestas
    # ────────────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("🤖 Entrenando IA (Random Forest)...")
    modelo_rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        class_weight="balanced",
        random_state=42
    )
    modelo_rf.fit(X_train, y_train)

    # ── Métricas reales sobre el conjunto de prueba ──
    y_pred       = modelo_rf.predict(X_test)
    y_proba_test = modelo_rf.predict_proba(X_test)[:, 1]

    auc          = roc_auc_score(y_test, y_proba_test)
    report_dict  = classification_report(y_test, y_pred, output_dict=True)
    cm           = confusion_matrix(y_test, y_pred).tolist()
    fpr, tpr, _  = roc_curve(y_test, y_proba_test)

    print(f"\n📊 MÉTRICAS SOBRE TEST SET (20% del total):")
    print(f"   AUC-ROC  : {auc:.4f}")
    print(f"   Precisión: {report_dict['1']['precision']:.4f}")
    print(f"   Recall   : {report_dict['1']['recall']:.4f}")
    print(f"   F1-Score : {report_dict['1']['f1-score']:.4f}")
    print(f"   Matriz de confusión: {cm}")

    # ── Predecir probabilidades sobre TODO el dataset para scoring ──
    cust['probabilidad_churn'] = modelo_rf.predict_proba(X)[:, 1]

    # ── Guardar CSV de scoring ──
    path_salida = os.path.join(base_dir, "data", "clientes_scoring_precalculado.csv")
    cust.to_csv(path_salida, index=False)

    # ── Guardar importancia de features ──
    importancias = pd.Series(modelo_rf.feature_importances_, index=features_ml).to_dict()
    with open(os.path.join(base_dir, "data", "importancias.json"), 'w') as f:
        json.dump(importancias, f)

    # ── Guardar métricas del modelo para mostrar en el Dashboard ──
    metricas = {
        "auc_roc":   round(auc, 4),
        "precision": round(report_dict['1']['precision'], 4),
        "recall":    round(report_dict['1']['recall'], 4),
        "f1_score":  round(report_dict['1']['f1-score'], 4),
        "accuracy":  round(report_dict['accuracy'], 4),
        "confusion_matrix": cm,
        "roc_curve": {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist()
        },
        "train_size": len(X_train),
        "test_size":  len(X_test),
    }
    with open(os.path.join(base_dir, "data", "metricas_modelo.json"), 'w') as f:
        json.dump(metricas, f, indent=2)

    print("\n🎯 ¡Pipeline completado! Archivos generados en data/:")
    print("   · clientes_scoring_precalculado.csv")
    print("   · importancias.json")
    print("   · metricas_modelo.json  ← NUEVO")

if __name__ == "__main__":
    ejecutar_entrenamiento_ia()