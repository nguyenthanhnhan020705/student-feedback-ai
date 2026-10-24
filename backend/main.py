from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from backend.routes import health, predict

app = FastAPI(
    title="Student Feedback AI API",
    version="1.0.0",
    description="API Phân tích cảm xúc và phân loại chủ đề phản hồi sinh viên"
)

# Custom xử lý lỗi 422 Validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu đầu vào không hợp lệ.",
                "details": jsonable_encoder(exc.errors())
            }
        }
    )

# Khai báo các đường dẫn API
app.include_router(health.router, prefix="/api")
app.include_router(predict.router, prefix="/api")