# AstroAI-Core

🌌 **AI-Powered Astronomy Data Analysis Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Development](https://img.shields.io/badge/status-development-orange.svg)]()

---

## 🚀 Overview

AstroAI-Core is an open-source platform that combines deep learning with astronomical data to help enthusiasts and researchers:

- 🔭 **Detect Exoplanets** - Automatic transit signal detection from TESS/Kepler light curves
- ⭐ **Classify Stars** - AI-powered stellar classification (OBAFGKM)
- 🌌 **Identify Anomalies** - Discover rare and unusual celestial objects
- 📊 **Analyze Spectra** - Automated spectral analysis and redshift measurement

---

## ✨ Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Light Curve Analysis | Process TESS/Kepler time-series data | 🚧 Developing |
| Image Classification | Automatic star/galaxy/nebula classification | 📋 Planned |
| Anomaly Detection | Unsupervised discovery of unusual objects | 📋 Planned |
| Spectral Analysis | Stellar spectrum classification | 📋 Planned |
| Interactive Visualization | 3D star maps and charts | 📋 Planned |
| RESTful API | Programmatic access to all features | 📋 Planned |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│         Web App │ Mobile App │ CLI │ API Client             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│              Auth │ Rate Limit │ Routing                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Microservices                             │
│    Data Service │ Model Service │ User Service │ Job Service│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│        PostgreSQL │ Redis │ MinIO/S3 │ DuckDB               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Data Sources                      │
│         NASA API │ ESA API │ SDSS │ Other Archives          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 + TypeScript + Three.js |
| **Backend** | Python 3.11 + FastAPI |
| **ML Framework** | PyTorch 2.0 + HuggingFace |
| **Database** | PostgreSQL 15 + Redis 7 |
| **Storage** | MinIO / AWS S3 |
| **Deployment** | Docker + Kubernetes |
| **Monitoring** | Prometheus + Grafana |

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/AstroAI-Core.git
cd AstroAI-Core

# Set up backend
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install

# Start development environment
cd ..
docker-compose up -d
```

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/astroai
REDIS_URL=redis://localhost:6379

# API Keys
NASA_API_KEY=your_nasa_api_key
ESA_API_KEY=your_esa_api_key

# JWT Secret
JWT_SECRET=your_secret_key

# Storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

---

## 📖 Usage

### Python SDK

```python
from astroai import AstroAIClient

# Initialize client
client = AstroAIClient(api_key="your_api_key")

# Analyze light curve
result = client.analyze_lightcurve(
    data=[...],  # Your flux measurements
    cadence=1800  # seconds
)
print(f"Exoplanet probability: {result.planet_probability:.2%}")
print(f"Estimated period: {result.period:.2f} days")

# Classify star image
result = client.classify_image("star_photo.png")
print(f"Spectral type: {result.spectral_type}")
print(f"Luminosity class: {result.luminosity_class}")
```

### REST API

```bash
# Analyze light curve
curl -X POST http://localhost:8000/api/v1/analyze/lightcurve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": [...], "cadence": 1800}'

# Get object information
curl http://localhost:8000/api/v1/objects/TOI-700 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Web Interface

Open your browser and navigate to `http://localhost:3000`

---

## 📊 Data Sources

AstroAI-Core integrates with multiple astronomical data archives:

| Source | Data Type | Access |
|--------|-----------|--------|
| **NASA TESS** | Exoplanet transit data | Public API |
| **NASA Kepler** | Confirmed exoplanets | MAST API |
| **NASA Hubble** | Deep space images | MAST API |
| **ESA Gaia** | Star positions & proper motions | ESA Archive |
| **SDSS** | Galaxy/stellar spectra | CASJobs |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit code fixes
- 🧪 Test beta releases

### Development Setup

```bash
# Fork and clone
git fork https://github.com/your-org/AstroAI-Core
git clone https://github.com/your-username/AstroAI-Core.git

# Create branch
git checkout -b feature/your-feature-name

# Make changes and commit
git commit -m "feat: add your feature"

# Push and create PR
git push origin feature/your-feature-name
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- NASA Exoplanet Archive for open data access
- ESA Gaia mission for stellar catalog
- The astronomy community for continuous support
- All contributors and supporters

---

## 📬 Contact

- **Website**: [Coming Soon]
- **Discord**: [Join our community]
- **Twitter**: [@AstroAI_Core]
- **Email**: contact@astroai-core.dev

---

## 🗺️ Roadmap

### Phase 1 (Q2 2026): MVP
- [x] Project setup
- [ ] Core ML models
- [ ] Basic API
- [ ] Web interface

### Phase 2 (Q3 2026): Feature Complete
- [ ] Image classification
- [ ] Anomaly detection
- [ ] User system
- [ ] Documentation

### Phase 3 (Q4 2026): Production Ready
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Beta testing
- [ ] Public launch

---

<div align="center">

**Made with ❤️ by the AstroAI Team**

🌟 *Exploring the universe with AI* 🌟

</div>
