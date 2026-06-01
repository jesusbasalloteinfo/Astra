# Chapter 3: The Hardware Bridge (Device Management and Connection)

Astra does not just work in isolation; it can connect to your astronomical equipment (telescope, mount, camera, etc.). In this chapter, you'll learn how to "pair" your hardware and how to configure each component so the application can use your equipment.

## 3.1 The "Device" Concept in Astra
In Astra, a **Device** is usually a control unit (like a Raspberry Pi or a computer with the INDI server and Astra Edge) that acts as a gateway between the Internet and your telescope.

### Token (PIN) Pairing
For security reasons, we use a pairing system to connect with your device:
1.  Go to the **Devices** section in the side menu.
2.  Press the **"+ Pair a device"** button.
3.  Enter the **Token or PIN** provided by your device.
4.  Press **"Pair"**. Astra will look for the device and add it to your permanent list.

## 3.2 The Device Card
Each paired device appears as a card with real-time information:
*   **Custom Name:** You can change the device's name (e.g., "Garden Setup") by pressing the pencil icon.
*   **Connection Status:**
    *   **Online (Green):** The device is powered on and connected to the Internet.
    *   **Offline (Red):** The device is not available. Check your server's power and network.
*   **Device ID:** A unique identification code.

## 3.3 Selection of INDI Components
Once the device is **Online**, Astra will detect all the equipment that the INDI server is managing. This is where you have to tell Astra which device components you want to use.

### How to configure the components:
Inside the active device card, you'll see selectors for:
1.  **Telescope / Mount:** Select your mount's name (e.g., "Celestron GPS" or "SkyWatcher"). This will allow Astra to send movement commands (Slew).

**Note:** Astra saves these preferences. The next time you connect the device, it will already know which components to use by default.

## 3.4 Management and Security
*   **Activating a Device:** Simply click on the card of the device you want to use. Astra will mark it as **ACTIVE**.
*   **Removing a Device:** If you no longer use a setup, you can unpair it by pressing the trash can icon. You'll have to confirm the action to avoid accidental losses.

This step is vital: **Without an active device and a selected telescope, you won't be able to use the device control functions.**

---
