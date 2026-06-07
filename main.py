import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import qrcode
import io
import base64

app = FastAPI(title="QR Code Generator API", version="1.0.0")
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

security = HTTPBearer()

API_KEY=*** "default-dev-key-change-in-production")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

class QRRequest(BaseModel):
    data: str = Field(..., min_length=1, max_length=2048, description="Text or URL to encode")
    size: int = Field(256, ge=64, le=2048, description="Image size in pixels")
    border: int = Field(4, ge=0, le=20, description="Border modules")
    color: str = Field("#000000", description="Foreground color (hex)")
    bg_color: str = Field("#FFFFFF", description="Background color (hex)")
    format: str = Field("png", description="Output format: png or svg")

class QRResponse(BaseModel):
    success: bool
    format: str
    data: str = None
    size: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate_qr(req: QRRequest, _: str = Depends(verify_api_key)):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=max(1, req.size // 20),
            border=req.border,
        )
        qr.add_data(req.data)
        qr.make(fit=True)

        if req.format == "svg":
            import qrcode.image.svg
            img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
            stream = io.BytesIO()
            img.save(stream)
            svg_data = stream.getvalue().decode("utf-8")
            return QRResponse(success=True, format="svg", data=svg_data, size=req.size)
        else:
            img = qr.make_image(fill_color=req.color, back_color=req.bg_color)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return QRResponse(success=True, format="base64", data=img_str, size=req.size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    pass