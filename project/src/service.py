import os
import pickle
import logging
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from catboost import CatBoostClassifier
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Telecom Churn Prediction API", version="1.0")

model = None
scaler = None
feature_columns = None

@app.on_event("startup")
def load_artifacts():
    global model, scaler, feature_columns
    try:
        logger.info("Загрузка артефактов...")
        model = CatBoostClassifier()
        model.load_model("../artifacts/catboost_churn_model.cbm")
        
        with open("../artifacts/scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
            
        with open("../artifacts/features.pkl", "rb") as f:
            feature_columns = pickle.load(f)
            
        logger.info("Артефакты успешно загружены.")
    except Exception as e:
        logger.error(f"Ошибка загрузки артефактов: {e}")
        raise e

# --- НОВОЕ: Автоматический редирект на документацию ---
@app.get("/", include_in_schema=False)
def root_redirect():
    """Перенаправляет пользователя с корневого URL на Swagger UI"""
    return RedirectResponse(url="/docs")
# --------------------------------------------------------

@app.get("/health")
def health_check():
    logger.info("GET /health -> {'status': 'ok'}")
    return {"status": "ok", "model_loaded": model is not None}

class CustomerData(BaseModel):
    gender: str = "Male"
    SeniorCitizen: int = 0
    Partner: str = "Yes"
    Dependents: str = "No"
    tenure: int = 12
    PhoneService: str = "Yes"
    MultipleLines: str = "No"
    InternetService: str = "Fiber optic"
    OnlineSecurity: str = "No"
    OnlineBackup: str = "Yes"
    DeviceProtection: str = "No"
    TechSupport: str = "No"
    StreamingTV: str = "Yes"
    StreamingMovies: str = "Yes"
    Contract: str = "Month-to-month"
    PaperlessBilling: str = "Yes"
    PaymentMethod: str = "Electronic check"
    MonthlyCharges: float = 89.9
    TotalCharges: float = 1080.5


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str


@app.post("/predict", response_model=PredictionResponse)
def predict(data: CustomerData):
    req_id = os.urandom(4).hex()
    logger.info(f"POST /predict id={req_id} status=received")
    
    try:
        df = pd.DataFrame([data.model_dump()]) # Используем model_dump() вместо устаревшего dict()
        df_encoded = pd.get_dummies(df)
        
        df_aligned = pd.DataFrame(columns=feature_columns)
        for col in df_aligned.columns:
            if col in df_encoded.columns:
                df_aligned[col] = df_encoded[col]
            else:
                df_aligned[col] = 0
                
        num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
        df_aligned[num_cols] = scaler.transform(df_aligned[num_cols])
        
        pred_class = int(model.predict(df_aligned)[0])
        pred_proba = float(model.predict_proba(df_aligned)[0][1])
        
        logger.info(f"POST /predict id={req_id} status=200 churn={pred_class}")
        
        # Возвращаем данные через новую схему
        return PredictionResponse(
            prediction=pred_class,
            probability=round(pred_proba, 4),
            model_version=os.getenv("MODEL_VERSION", "v1.0")
        )
    except Exception as e:
        logger.error(f"POST /predict id={req_id} status=500 error='{str(e)}'")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
