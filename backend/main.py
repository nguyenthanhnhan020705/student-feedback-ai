
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.routes import health, predict

app = FastAPI(
    title="Student Feedback AI API",
    version="1.0.0",
    description="API phân tích cảm xúc và phân loại chủ đề phản hồi sinh viên",
)


def make_error_response(
    code: str,
    message: str,
    details: list[dict[str, str]],
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "contract_version": "1.0",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    details = []
    body = exc.body
    errors = exc.errors()

    if any(error.get("type") == "json_invalid" for error in errors):
        details.append({"field": "$body", "reason": "invalid_json"})

    elif not isinstance(body, dict):
        details.append({"field": "$body", "reason": "type"})

    else:
        field_order = {
            key: index for index, key in enumerate(body.keys())
        }

        for error in errors:
            loc = error.get("loc", ())
            field = str(loc[-1]) if loc else "$body"
            error_type = error.get("type", "")

            if field == "text":
                if error_type == "missing":
                    reason = "required"
                elif error_type == "string_too_long" or (
                    error_type == "value_error"
                    and "too_long" in str(error.get("ctx", {}))
                ):
                    reason = "too_long"
                elif error_type == "string_type":
                    reason = "type"
                elif error_type == "value_error":
                    reason = "blank"
                else:
                    reason = "type"

            elif error_type == "extra_forbidden":
                reason = "extra_field"

            else:
                reason = "type"

            details.append({"field": field, "reason": reason})

        details.sort(
            key=lambda item: (
                field_order.get(item["field"], len(field_order)),
                item["field"],
            )
        )

    return make_error_response(
        code="INVALID_INPUT",
        message="Dữ liệu đầu vào không hợp lệ.",
        details=details,
        status_code=422,
    )


app.include_router(health.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
