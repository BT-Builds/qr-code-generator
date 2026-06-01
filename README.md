# QR Code Generator API

Generate QR codes on-demand via HTTP API.

## Endpoints

### POST /generate
Generate a QR code from text or URL.

**Headers:** `Authorization: Bearer <API_KEY>`

**Body:**
```json
{
  "data": "https://example.com",
  "size": 256,
  "border": 4,
  "color": "#000000",
  "bg_color": "#FFFFFF",
  "format": "png"
}
```

**Response:**
```json
{
  "success": true,
  "format": "base64",
  "data": "iVBORw0KGgoAAAANSUhEUg...",
  "size": 256
}
```

### GET /health
Health check endpoint (no auth required).

## Usage

```bash
curl -X POST https://qr-code-generator-mu-blush.vercel.app/generate \\
  -H "Authorization: Bearer default-dev-key-change-in-production" \\
  -H "Content-Type: application/json" \\
  -d '{"data": "Hello World"}'
```

## Monetize
- RapidAPI: $19/month for 10k requests
- Direct subscriptions via ExtensionPay