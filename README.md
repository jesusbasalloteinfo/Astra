<div align="center">
  <img src="assets/astra_main.svg" alt="ASTRA Logo" width="200">  
  <p>
    <strong>Automated Smart Telescope Remote Assistant</strong>
  </p>
  
  <p>
  <p>
    <img src="https://img.shields.io/badge/License-AGPL_v3-orange.svg" alt="License: AGPL v3">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/docker-ready-green" alt="Docker">
  </p>
</div>

---

**ASTRA** is an open-source **Unified Astronomy Platform** designed to simplify the control of astronomical equipment for amateur astronomers.

This project serves as a comprehensive hardware hub, bridging the gap between complex astronomical instruments and modern software. By combining a responsive **Svelte-based** interface with the standard **INDI protocol**, it allows users to orchestrate telescopes and mounts through a powerful UI or an integrated **AI-powered assistant**.

## How it works 🔭

You can interact with your setup using the dashboard or by sending natural language commands. Here are some examples of what you can do:

*   **Targeting:** *"Slew to the Andromeda Galaxy"* or *"Point to M42"*.
*   **Discovery:** *"What are the brightest nebulae visible tonight?"*
*   **Status:** *"Check telescope alignment status"* or *"Is my telescope currently parked?"*.


## Core Architecture
The system is built with a hybrid IoT approach to ensure both performance and flexibility:
*   **Edge Hardware Control:** Native hardware control with a **Raspberry Pi** for reliable, low-latency device management.
*   **Containerized Stack:** The web interface and AI engine operate in **Docker** containers, ensuring a modular, scalable, and robust deployment.
*   **Intuitive Control:** Control your equipment your way, manually through the dashboard or via **Natural Language** to automate complex observation workflows.

## Quick Start 🚀

The easiest way to get **ASTRA** up and running is using **Docker Compose**. 

### Prerequisites
- INDI-compatible astronomical gear
- A **Raspberry Pi** (recommended for hardware control).
- **Docker** and **Docker Compose** installed.

### Installation
1. **Clone the repository:**
    ```bash
    git clone https://github.com
    cd astra
    ```
2. **Configure your environment:**
    Copy the example environment file and add your specific configuration (e.g., API keys for the LLM if needed):
    ```bash
    cp .env.example .env
    ```

3. **Launch the platform:**
    ```bash
    docker compose up -d
    ```

4. **Access the UI:**
Open your browser and navigate to [http://localhost:4000](http://localhost:4000).
