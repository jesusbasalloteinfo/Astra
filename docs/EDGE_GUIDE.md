# Astra Edge Setup Guide 🛰️

The **Astra Edge** node is the component that runs locally on your observatory computer (typically a Raspberry Pi) and communicates directly with your astronomical hardware via the INDI protocol.

## 1. Hardware Requirements

*   **Computer:** Raspberry Pi 4 or 5 is recommended for optimal performance, especially if using high-resolution cameras.
*   **Operating System:** Any Linux distribution (Raspberry Pi OS, Ubuntu, Debian). Testing has been made in a Raspberry Pi running Ubuntu.
*   **Connectivity:** 
    *   USB ports for telescope and camera connections.
    *   Stable Internet connection (WiFi or Ethernet) to communicate with the Central Astra Server.
*   **Power:** Ensure your Pi has a high-quality power supply

## 2. Installing INDI Library

Astra Edge relies on the **INDI Library** to talk to your hardware. You must install the INDI server and the specific drivers for your equipment.

Follow the official installation instructions for your platform here:
👉 **[Official INDI Download & Installation Guide](https://indilib.org/download.html)**


## 3. Setting Up Astra Edge

Once INDI is installed, you need to install the Astra Edge client.

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/your-username/astra-project.git
    cd astra-project/astra_edge
    ```
2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

## 4. Configuration

Astra Edge can be configured via environment variables in a `.env` file or via command-line arguments.

### Using `.env` file
Create a `.env` file in the `astra_edge` directory:
```env
ASTRA_URL=http://your-astra-server/api
INDI_HOST=127.0.0.1
INDI_PORT=7624
INDI_DRIVERS="indi_celestron_gps indi_asi_ccd"  # Space-separated list of drivers
LAT=41.38
LON=2.17
```

### Command Line Arguments
Alternatively, you can pass parameters directly:
```bash
python astra_edge.py --astra-url http://your-astra-server/api --drivers indi_celestron_gps indi_asi_ccd
```

## 5. First Run & Pairing

1.  **Start the client:** `python astra_edge.py`
2.  **Look for the Pairing Code:** On the first run, Astra Edge will display a 6-digit code in the terminal.
3.  **Link to your account:**
    *   Log in to your Astra web dashboard.
    *   Navigate to **Devices > Pair New Device**.
    *   Enter the code displayed on the terminal.
4.  **Automatic Reconnect:** Once paired, the credentials will be stored in `edge_auth.json`. The next time you start the client, it will connect automatically.

## 6. Automating with systemd (Optional but Recommended)

To ensure Astra Edge starts automatically when the Raspberry Pi boots:

1.  Create a service file: `sudo nano /etc/systemd/system/astra-edge.service`
2.  Paste the following (adjust paths to your installation):
    ```ini
    [Unit]
    Description=Astra Edge Client
    After=network.target

    [Service]
    ExecStart=/home/pi/astra-project/astra_edge/venv/bin/python /home/pi/astra-project/astra_edge/astra_edge.py
    WorkingDirectory=/home/pi/astra-project/astra_edge
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=pi

    [Unit]
    [Install]
    WantedBy=multi-user.target
    ```
3.  Enable and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable astra-edge
    sudo systemctl start astra-edge
    ```

---
*For software architecture details, see [Architecture Guide](ARCHITECTURE.md).*
