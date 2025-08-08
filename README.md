# Autonomous Agent System

Sistem agent otomatis dengan kemampuan browser automation yang dapat beroperasi dalam lingkungan sandbox menggunakan Docker. Agent ini menggunakan Large Language Model (LLM) untuk perencanaan dan dapat melakukan berbagai tugas web automation secara otomatis.

## 🚀 Fitur Utama

- **Lingkungan Sandbox**: Berjalan dalam container Docker yang terisolasi dan aman
- **LLM Integration**: Mendukung OpenAI GPT dan Anthropic Claude untuk perencanaan cerdas
- **Browser Automation**: Menggunakan Playwright untuk kontrol browser yang powerful
- **Loop Perencanaan-Eksekusi-Observasi**: Siklus otomatis untuk mencapai tujuan
- **RESTful API**: Interface HTTP untuk integrasi dengan aplikasi lain
- **Toolset Lengkap**: Kumpulan tools untuk navigasi, klik, input, dan pembacaan DOM

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request (HTTP API)                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Agent Orchestrator                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ LLM Interface│  │Planning Logic│  │      Toolset           │  │
│  │(OpenAI/Claude)│  │             │  │ • navigate()           │  │
│  └─────────────┘  └─────────────┘  │ • click()              │  │
│                                    │ • type()               │  │
│                                    │ • read_dom()           │  │
│                                    │ • wait()               │  │
│                                    └─────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                Docker Sandbox Environment                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Browser Manager (Playwright)               │    │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │    │
│  │  │ Browser Instance │◄──►│        Web Page (DOM)       │ │    │
│  │  │   (Chromium)    │    │                             │ │    │
│  │  └─────────────────┘    └─────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Persyaratan Sistem

- **Docker**: Untuk menjalankan lingkungan sandbox
- **Python 3.11+**: Untuk aplikasi utama
- **API Key**: OpenAI atau Anthropic untuk LLM functionality

## 🛠️ Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd autonomous-agent
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env file dengan API keys Anda
```

### 3. Build Docker Image

```bash
docker build -t autonomous-agent .
```

### 4. Run dengan Docker Compose

```bash
docker-compose up -d
```

### 5. Instalasi Lokal (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run server
python start_server.py
```

## 🎯 Penggunaan

### API Endpoints

#### 1. Health Check
```http
GET /
```

#### 2. Execute Agent Task
```http
POST /agent/execute
Content-Type: application/json

{
    "goal": "Navigate to example.com and read the page content",
    "max_iterations": 5,
    "timeout": 300
}
```

#### 3. Get Agent Status
```http
GET /agent/status
```

#### 4. Stop Current Task
```http
POST /agent/stop
```

### Contoh Penggunaan dengan Python

```python
import requests

# Execute task
response = requests.post("http://localhost:8000/agent/execute", json={
    "goal": "Navigate to Google and search for 'autonomous agent'",
    "max_iterations": 10
})

result = response.json()
print(f"Status: {result['status']}")
print(f"Steps: {len(result['steps'])}")
```

### Contoh Penggunaan dengan cURL

```bash
# Execute simple navigation task
curl -X POST "http://localhost:8000/agent/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "goal": "Navigate to example.com and take a screenshot",
       "max_iterations": 3
     }'
```

## 🔧 Konfigurasi

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key untuk GPT models | - |
| `ANTHROPIC_API_KEY` | Anthropic API key untuk Claude models | - |
| `LLM_PROVIDER` | Provider LLM (openai/anthropic) | openai |
| `BROWSER_TYPE` | Jenis browser (chromium/firefox/webkit) | chromium |
| `HEADLESS` | Mode headless browser (true/false) | true |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

### Toolset Configuration

Agent dilengkapi dengan toolset berikut:

- **navigate(url)**: Navigate ke URL tertentu
- **click(selector)**: Klik element berdasarkan CSS selector
- **type(selector, text)**: Input text ke field
- **read_dom()**: Baca dan ringkas DOM page
- **wait(seconds)**: Wait untuk durasi tertentu

## 🧪 Testing

### Run All Tests

```bash
python test_agent.py
```

### Run Demo

```bash
python demo.py
```

### Manual Testing

```bash
# Start server
python start_server.py

# Test dengan browser
curl http://localhost:8000/
```

## 📁 Struktur Project

```
autonomous-agent/
├── agent/
│   ├── __init__.py
│   ├── models.py              # Data models
│   ├── llm_interface.py       # LLM integration
│   ├── browser_manager.py     # Browser automation
│   ├── toolset.py            # Available tools
│   └── orchestrator.py       # Main agent loop
├── logs/                     # Log files
├── data/                     # Data storage
├── screenshots/              # Screenshots
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── main.py                 # FastAPI application
├── start_server.py         # Server startup script
├── test_agent.py           # Test suite
├── demo.py                 # Demo script
└── README.md               # Documentation
```

## 🔍 Troubleshooting

### Common Issues

1. **Browser tidak bisa start**
   - Pastikan Docker memiliki akses ke display (untuk non-headless mode)
   - Check apakah Playwright browsers sudah terinstall

2. **LLM API Error**
   - Verify API key sudah benar
   - Check quota dan billing account
   - Pastikan model yang digunakan tersedia

3. **Permission Denied**
   - Pastikan user memiliki akses ke Docker
   - Check file permissions untuk direktori project

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
python start_server.py
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) untuk browser automation
- [FastAPI](https://fastapi.tiangolo.com/) untuk web framework
- [OpenAI](https://openai.com/) dan [Anthropic](https://anthropic.com/) untuk LLM APIs

