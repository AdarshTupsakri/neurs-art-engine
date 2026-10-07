# NEURS Art Engine 🎨🚀

> **"Teaching Anyone to Create Art, Step by Step"**  
> Developed at Woxsen University under Prof. Geeta Tripathi  
> Team: Akhil Uppula, Akshay Jai, Trilochan Singh, Adarsh Tupsakri

---

## 🌟 Overview

**NEURS Art Engine** is a full-stack, AI-powered interactive art tutorial platform. It breaks down complex visual artwork—ranging from retro Pixel Art to fine Sketching and Painterly atelier layers—into cumulative, progressive step-by-step visual construction orders.

Learners can scrub forward and backward through construction stages, inspect layer breakdowns, toggle onion skinning (ghosting), and learn traditional and digital art techniques interactively on a high-performance HTML5 Canvas editor.

---

## 🏗 System Architecture

- **Backend**: FastAPI (Python 3.11+), OpenCV, Pillow, Google Gemini API, hosted on **Railway**.
- **Frontend**: React 18, Vite, TypeScript, HTML5 `<canvas>` buffer engine with zero interaction latency, hosted on **Cloudflare Pages**.
- **Generation Pipelines**:
  1. **Pixel Art Engine**: Deterministic sprite grid sheet generation and slicing.
  2. **Cumulative Sketching Engine**: 5-stage scaffolding build order (Gesture -> Primary Silhouette -> Plane Breaks -> Hatching -> Fine Accents).
  3. **Painterly Layering Engine**: Digital atelier underpainting & value layering (Imprimatura -> Grisaille Block-in -> Local Color -> Form Modeling -> Specular Highlights).

---

## 📂 Project Structure

```
neurs-art-engine/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints (sketch, paint, pixel, upload)
│   │   │   ├── sketch.py
│   │   │   ├── paint.py
│   │   │   ├── pixel.py
│   │   │   └── health.py
│   │   ├── core/                # App config, CORS, logging
│   │   │   └── config.py
│   │   ├── services/
│   │   │   ├── gemini_service.py # Prompting & batch generation
│   │   │   ├── sketch_engine.py  # Cumulative visual sketching decomposition
│   │   │   ├── paint_engine.py   # Underpainting & painterly value layering
│   │   │   └── slice_processor.py# Deterministic sheet slicing & registration
│   │   └── main.py
│   ├── tests/                   # Visual continuity & unit test suite
│   │   ├── test_sketch_engine.py
│   │   ├── test_paint_engine.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CanvasEditor.tsx # High-performance HTML Canvas engine
│   │   │   ├── LayerPanel.tsx   # Layer toggle, opacity, order controls
│   │   │   ├── StepReplay.tsx   # Step-by-step tutorial scrub bar
│   │   │   └── ModeSelector.tsx # Pixel Art / Sketching / Painting
│   │   ├── types/
│   │   │   └── art.ts           # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── create_repo.py               # GitHub repository creation & push automation
├── .gitignore
└── README.md
```

---

## ⚙️ Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+ / npm

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend will run at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will launch at `http://localhost:5173`.

---

## 🧪 Running Tests

To verify backend services and cumulative visual continuity:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 🚀 Deployment

- **Railway (Backend)**: Connect repository `neurs-art-engine`, root directory `/backend`, railway will auto-detect `railway.json` / `Dockerfile`.
- **Cloudflare Pages (Frontend)**: Framework preset `Vite`, build command `npm run build`, output directory `dist`, root directory `/frontend`.

---

## 📜 License & Acknowledgments

Developed at Woxsen University under guidance of **Prof. Geeta Tripathi**.  
Released under the MIT License.
