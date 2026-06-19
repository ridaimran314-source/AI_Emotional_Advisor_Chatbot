# AI Emotional Advisor Chatbot

A simple, supportive AI-powered emotional advisor web app. Users can chat about stress, sadness, loneliness, and everyday life challenges in a calm, friendly interface.

**Important:** This app provides general emotional support only. It is **not** a medical product, does not diagnose conditions, and does not replace professional mental health care.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (no framework)
- **Backend:** Python Flask
- **AI:** Configurable provider via `.env` (Groq recommended for development)

## Default AI Provider: Groq

This project defaults to **Groq** with the `llama-3.1-8b-instant` model because:

- Free tier available for development
- Very fast response times
- Good quality for conversational emotional support
- Simple OpenAI-compatible API

You can switch to Gemini, OpenRouter, or Hugging Face by changing `AI_PROVIDER` and `AI_MODEL` in `.env` — no frontend changes required.

## Project Structure

```
ai-emotional-advisor-chatbot/
├── app.py                  # Flask routes and API endpoint
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── services/
    ├── ai_service.py       # Configurable AI provider calls
    └── safety_service.py   # Crisis keyword detection
```

## Setup

### 1. Clone and create virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example file and add your API key:

```bash
copy .env.example .env
```

Edit `.env` and set at minimum:

```env
AI_PROVIDER=groq
AI_API_KEY=your_groq_api_key_here
AI_MODEL=llama-3.1-8b-instant
```

Get a free Groq API key at [https://console.groq.com](https://console.groq.com).

### 4. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Switching AI Providers

Set `AI_PROVIDER` in `.env` to one of:

| Provider     | `AI_PROVIDER` value | Example `AI_MODEL`                    |
|-------------|---------------------|---------------------------------------|
| Groq        | `groq`              | `llama-3.1-8b-instant`                |
| Google Gemini | `gemini`          | `gemini-1.5-flash`                    |
| OpenRouter  | `openrouter`        | `meta-llama/llama-3.1-8b-instruct:free` |
| Hugging Face | `huggingface`      | `microsoft/DialoGPT-medium`           |

Restart the Flask server after changing `.env`.

## API

### `POST /api/chat`

**Request:**
```json
{
  "message": "I've been feeling really stressed lately.",
  "mood": "stressed"
}
```

**Response:**
```json
{
  "success": true,
  "reply": "I hear you...",
  "mood": "stressed",
  "is_crisis": false
}
```

## Safety Features

- **Crisis keyword detection** runs before any AI API call (e.g. suicide, self-harm phrases)
- Crisis messages receive an immediate safety response without relying solely on the AI
- Rate limiting: 20 requests per minute per IP on `/api/chat`
- API keys are server-side only — never exposed to the browser
- Input validation: empty and overly long messages are rejected

## Deployment (Basic)

For production:

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (e.g. Gunicorn on Linux):

   ```bash
   pip install gunicorn
   gunicorn -w 2 -b 0.0.0.0:5000 app:app
   ```

3. Serve over **HTTPS** (e.g. behind Nginx or a cloud platform)
4. Set a strong `FLASK_SECRET_KEY`
5. Never commit `.env` — use your host's secret/environment variable management

Platforms like Render, Railway, or PythonAnywhere work well for small Flask apps.

## Testing Checklist

- [ ] Normal sad message returns supportive advice
- [ ] Stress message returns practical calming steps
- [ ] Empty message shows validation error
- [ ] Very long message (>1000 chars) is blocked
- [ ] Crisis/self-harm message returns urgent safety response
- [ ] Invalid API key shows friendly error
- [ ] Frontend works on desktop and mobile
- [ ] API key is not visible in browser network responses

## License

For educational and personal use. Always seek professional help for serious mental health concerns.
