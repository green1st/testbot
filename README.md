# Autonomous Agent - AI Browser Automation

Sistem agent otomatis yang dapat melakukan browser automation dengan antarmuka pengguna yang canggih, mirip dengan Manus.ai.

## 🚀 Fitur Utama

### Backend Agent
- **Browser Automation**: Menggunakan Playwright untuk kontrol browser otomatis
- **LLM Integration**: Mendukung OpenAI GPT dan Anthropic Claude
- **Loop Perencanaan-Eksekusi-Observasi**: Siklus otomatis untuk mencapai tujuan
- **RESTful API**: Interface HTTP untuk integrasi
- **WebSocket Support**: Real-time updates dan komunikasi

### Frontend UI
- **Modern React Interface**: Antarmuka pengguna yang responsif dan intuitif
- **Real-time Monitoring**: Melihat progress agent secara langsung
- **Task Builder**: Template untuk membuat task dengan mudah
- **Screenshot Viewer**: Melihat screenshot browser saat agent bekerja
- **Task History**: Riwayat task yang pernah dijalankan
- **Execution Logs**: Log detail dari setiap langkah eksekusi

### Kemampuan Agent
- **Navigate**: Browse ke website tertentu
- **Click**: Klik elemen di halaman web
- **Type**: Mengisi form dan input field
- **Read DOM**: Membaca dan mengekstrak konten halaman
- **Wait**: Menunggu elemen atau kondisi tertentu
- **Screenshot**: Mengambil screenshot halaman

## 📁 Struktur Proyek

```
autonomous-agent/
├── agent/                  # Backend agent modules
│   ├── browser_manager.py  # Playwright browser management
│   ├── llm_interface.py    # LLM integration
│   ├── orchestrator.py     # Main agent orchestrator
│   ├── toolset.py         # Agent tools
│   └── models.py          # Data models
├── agent-ui/              # Frontend React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API services
│   │   └── App.jsx        # Main application
│   └── package.json       # Frontend dependencies
├── main.py                # FastAPI backend server
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
└── README.md             # This file
```

## 🛠️ Instalasi

### Metode 1: Docker (Disarankan)

1. **Clone repository**:
   ```bash
   git clone https://github.com/green1st/testbot.git
   cd testbot
   ```

2. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env dan isi API keys Anda
   ```

3. **Jalankan dengan Docker**:
   ```bash
   docker-compose up -d
   ```

4. **Akses aplikasi**:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000

### Metode 2: Instalasi Lokal

1. **Clone repository**:
   ```bash
   git clone https://github.com/green1st/testbot.git
   cd testbot
   ```

2. **Setup Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env dan isi API keys Anda
   ```

4. **Jalankan backend**:
   ```bash
   python start_server.py
   ```

5. **Jalankan frontend** (terminal baru):
   ```bash
   cd agent-ui
   npm install
   npm run dev
   ```

6. **Akses aplikasi**:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:5173

## 🔧 Konfigurasi

### Environment Variables

```ini
# OpenAI API Key (untuk GPT models)
OPENAI_API_KEY=sk-your_openai_api_key_here

# Anthropic API Key (untuk Claude models)  
ANTHROPIC_API_KEY=sk-ant-api03-your_anthropic_api_key_here

# Agent Configuration
LLM_PROVIDER=openai  # atau anthropic
BROWSER_TYPE=chromium  # chromium, firefox, atau webkit
HEADLESS=true  # true untuk headless mode, false untuk GUI mode

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 📖 Cara Penggunaan

### 1. Melalui Web UI

1. Buka http://localhost:3000 (atau port yang dikonfigurasi)
2. Ketik task yang ingin dilakukan di text area
3. Klik "Execute" untuk menjalankan task
4. Monitor progress melalui progress bar dan logs
5. Lihat hasil di task history

### 2. Melalui API

```bash
curl -X POST "http://localhost:8000/agent/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "goal": "Navigate to Google and search for autonomous agents",
       "max_iterations": 10
     }'
```

### 3. Contoh Task

- "Navigate to Google and search for autonomous agents"
- "Go to Amazon and search for wireless headphones, show me the top 5 results"
- "Visit https://example.com and extract all the contact information"
- "Fill out the contact form on https://example.com/contact with my information"

## 🔍 API Endpoints

- `GET /` - Health check
- `POST /agent/execute` - Execute agent task
- `GET /agent/status` - Get current agent status
- `POST /agent/stop` - Stop current task
- `WebSocket /ws` - Real-time updates

## 🧪 Testing

```bash
# Test backend
python test_agent.py

# Test frontend
cd agent-ui
npm test
```

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d --build
```

### Manual Deployment
1. Setup production environment variables
2. Build frontend: `cd agent-ui && npm run build`
3. Serve static files through backend
4. Run with production WSGI server

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - lihat file LICENSE untuk detail.

## 🆘 Troubleshooting

### Common Issues

1. **Browser tidak terbuka**: Pastikan Playwright browser terinstal
   ```bash
   python -m playwright install chromium
   ```

2. **API Key error**: Periksa file `.env` dan pastikan API key valid

3. **Port sudah digunakan**: Ubah port di konfigurasi atau hentikan service yang menggunakan port tersebut

4. **Frontend tidak terhubung ke backend**: Pastikan backend berjalan di port 8000 dan CORS dikonfigurasi dengan benar

### Support

Jika mengalami masalah, silakan buat issue di GitHub repository atau hubungi tim pengembang.

---

**Autonomous Agent** - Bringing AI-powered automation to your browser! 🤖✨

