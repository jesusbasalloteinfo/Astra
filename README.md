<div align="center">
  <img src="assets/astra_main.svg" alt="ASTRA Logo" width="300">  
  <p><strong>Automated Smart Telescope Remote Assistant</strong></p>

  <p>
    <img src="https://img.shields.io/badge/License-AGPL_v3-orange.svg" alt="License: AGPL v3">
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white" alt="Python Version">
    <img src="https://img.shields.io/badge/Svelte-5-ff3e00?logo=svelte&logoColor=white" alt="Svelte 5">
    <img src="https://img.shields.io/badge/FastAPI-005863?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker Ready">
  </p>
  
  <p><i>The unified, distributed platform for modern amateur astronomy.</i></p>
</div>


## 🌌 What is ASTRA?

**ASTRA** is an open-source **Unified Astronomy Platform** that bridges the gap between complex astronomical hardware and the modern web. It provides a complete ecosystem for remote observatory management, celestial discovery, and automated equipment control.

**Why was ASTRA built?**
Traditional astronomy setups often require a dedicated Windows (ASCOM) or Linux laptop running heavy desktop software (like KStars or Stellarium) right next to the telescope, filled with overwhelming buttons and complex configurations. ASTRA solves this by decoupling the hardware from the interface. 

With ASTRA, your equipment runs via a lightweight edge node, while you control everything from a clean, web-based dashboard on any device. More importantly, it features an integrated AI assistant designed for occasional observers: instead of fighting with menus or wondering what's up in the sky tonight, you can simply ask the assistant to find targets for you.


## ✨ Key Features

### 📡 Distributed Edge Control (`astra_edge`)
The heart of ASTRA's hardware integration. The **Edge Node** runs directly on your observatory computer (e.g., Raspberry Pi) and communicates natively with **INDI servers**.
- **Native INDI Integration:** Full control over telescopes, mounts, cameras, focusers, and filter wheels.
- **Hardware Abstraction:** Standardized interface for diverse equipment brands.
- **Remote Tunneling:** Securely connect your local hardware to the ASTRA cloud for global access.
- **Real-time Telemetry:** Low-latency monitoring of equipment status and environment.

### 🔭 Immersive 3D Dashboard
A high-performance web interface built with **Svelte 5** and **Three.js**.
- **3D Sky Visualization:** Real-time rendering of the celestial sphere and your equipment's orientation.
- **Responsive Control:** Manage your entire session from any device (Desktop, Tablet, Mobile).
- **Observation Management:** Plan, log, and review your sessions with ease.

### 📚 Sideris Physics & Catalog Engine
A dedicated service for precision astronomical calculations.
- **Massive Catalogs:** Instant access to thousands of stars and Deep Sky Objects (Messier, NGC, IC).
- **Precision Ephemerides:** High-accuracy position calculations for Solar System objects using `Astropy` and `SkyField`.
- **Visibility Planning:** "What's in the sky" calculations tailored to your specific location and time.

### 🤖 AI-Powered Assistance
An optional, model-agnostic layer to simplify complex workflows.
- **Natural Language Control:** "Can you suggest me what DSO objects could I see tonight?" or "What is the current altitude of Mars?"
- **Context-Aware Knowledge:** Integrated with Wikipedia and celestial catalogs to provide on-the-fly info about your targets.
- **Task Automation:** Streamline repetitive setup routines through text.


## 🏗️ Architecture

ASTRA uses a containerized microservices architecture:

- **astra_ui:** Modern Svelte 5 frontend with real-time 3D visualizations.
- **astra_api:** Central coordinator, session manager, and AI router.
- **astra_auth:** Secure JWT-based authentication and access control.
- **sideris:** High-performance celestial physics engine.
- **Kong Gateway:** Unified entry point and secure routing.


## 🛠️ Tech Stack

- **Frontend:** Svelte 5, TailwindCSS 4, Three.js, Lucide Icons, Paraglide-js (i18n).
- **Backend:** FastAPI, Python 3.11+, MongoDB (Core), PostgreSQL (LLM State).
- **Protocols:** INDI (Hardware), WebSockets (Real-time), REST (API).
- **DevOps:** Docker, Docker Compose, Kong Gateway.



## 🚀 Getting Started

For detailed deployment instructions and technical overview, please refer to the documentation:

- [🚀 Deployment Guide](docs/DEPLOY_GUIDE.md)
- [🏗️ Architecture Guide](docs/ARCHITECTURE.md)
- [🛰️ Edge Node (Hardware) Guide](docs/EDGE_GUIDE.md)
- [📖 User Guide](docs/user_guide/USER_GUIDE.md)



1. **Clone & Setup environment:**
   ```bash
   git clone https://github.com/your-username/astra-project.git
   cd astra-project
   cp example.env .env
   ```

2. **Launch:**
   ```bash
   docker compose up -d
   ```

3. **Explore:**
    Navigate to `http://localhost:8000` to access the unified dashboard.


## 📁 Project Structure

```text
├── astra_api/      # Core Backend (FastAPI)
├── astra_auth/     # Authentication Service
├── astra_edge/     # Hardware Abstraction Layer (INDI)
├── astra_ui/       # Svelte 5 Frontend
├── sideris/        # Catalog & Ephemerides Service
├── gateway/        # Kong Gateway Configuration
├── assets/         # Project Branding & Logos
└── docker-compose.yml
```


## 🌱 Project Status

ASTRA is a new project currently in active development! I am focusing on building the core features and am not quite ready to accept pull requests just yet. However, feel free to open an issue to share your feedback or report bugs.



## 📜 License

This project is licensed under the **AGPL v3 License** - see the [LICENSE](LICENSE) file for details.



<div align="center">
  <p>Clear skies and happy observing! 🔭</p>
</div>
