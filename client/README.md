# Rust Client

This Rust client uses the [btleplug](https://crates.io/crates/btleplug) library to connect with the scooter via Bluetooth Low Energy (BLE), retrieves data, and sends it to the server using MQTT. Additionally, it gathers GPS information.

Part of the code is based on the [m365 library](https://github.com/macbury/m365) developed by [macbury](https://github.com/macbury), as well as the reverse-engineered Xiaomi BLE protocol partially documented by [CamiAlfa](https://github.com/CamiAlfa/M365-BLE-PROTOCOL).

## Features

- **Bluetooth Low Energy:** Communicates with the scooter using BLE.
- **Supported scooters:** Compatible with the following Xiaomi models: m365, mi-lite-1-s, mi-pro, mi-pro2 and mi-pro3.
- **Reconnection Handling:** 
    - **MQTT and Scooter Reconnection:** The client handles reconnections to both MQTT broker (via the Paho-MQTT library) and the scooter.
    - **Initial scooter connection:** If the scooter isn't found initially, the client searched for a specific time before exiting. When configured, systemd will restart it inmediatly.
    - **Post-Login Reconnection:** If the connection is lost after login into the scooter, the client attempts to reconnect for some time before exiting. Short interruptions (normally less than 5 seconds) are handled by reusing the same session to avoid having to start the connection process from zero. By doing this the BLE micro-interruptions are "mitigated".
    - **Extended connection loss:** If in-client reconnection attempts fail after multiple tries, the client exits, triggering a systemd restart.

> **Note:** As this is a prototype, data collected while the client is disconnected from the broker is not stored. Offline storage may be considered 
in future updates. However, since data is collected at a high frequency (every few seconds), losing a small amount of data points should not be significant.

For details on setting up the systemd service, refer to the  [Raspberry installation guide](./../raspberry/README.md).

### 🚨 Important Note 🚨

**Pairing the scooter with this client will unpair it from all other devices.** 
If you wish to re-pair the scooter with the official Xiaomi app, you will need to reset it (a simple process that doesn't result in any data loss) and pair it again.

#### How to Reset the Scooter

1. Turn off the scooter.
2. Press and hold the following at the same time:
    - Power Button
    - Throttle
    - Brake lever
3. Keep these pressed until a red number appears on the screen.

Once done, you can re-pair the scooter with the Xiaomi app.

## How to compile the code

Ensure you have the Rust Toolchain installed, you can get more instructions on that [here](https://www.rust-lang.org/tools/install).
I compiled it on Ubuntu 24.04 and some other packages were required, including `libssl-dev pkg-config libdbus-1-dev cmake`

For convenience, a pre-compiled version of the client is available in the releases section (compiled for ARM64 in order to work with the Raspberry, and for x86_64).You can also compile the code yourself:

```bash
# From the current directory run:
cargo build --release
```

Once done, the `m365` executable will be located inside the `target/release` folder.

### Compiling for ARM devices

❗If you need to compile the client for a Raspberry Pi or other ARM devices, you have two options:

- Cross-compile from an x86-64 machine.
- Compile directly from an ARM64 device (e.g, using a Hetzner ARM VPS, as I did).

🚧 **Work in Progress:** Instructions on how to cross-compile for ARM devices will be added soon 🚧

## How to run the client

Before running the client, you will need to:

- Obtain the MAC address of the scooter.
- Generate a `.mi-token` file for authentication.

### Finding the scooter MAC address

There are multiple methods to get your scooter MAC address:

- If you already have it paired with your phone, you should be able to find the MAC on the Xiaomi APP.
- You can use an app like [nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile).
- You can use a little Rust program that finds Xiaomi Scooters, you can find the code in [examples/scanner.rs](examples/scanner.rs).

A pre-compiled version of the scanner is available in the releases section (either for x86_64 and ARM64). You can also compile/run the code yourself:

```bash
cargo run --example scanner
```
Example scanner output:
```
2022-03-01T20:24:52.433166Z DEBUG m365::scanner: Starting scanning for new devices
2022-03-01T20:24:52.445873Z DEBUG m365::scanner: Watching for events in background
2022-03-01T20:25:25.786072Z  INFO scanner: Found scooter nearby: MIScooterXXXX with mac: 00:1A:2B:3C:4D:5E
```

Once you have the scooter MAC, save it for later.

### Generating the .mi-token file

To connect to the scooter, you'll need an encryption key stored in a `.mi-token` file. I won't explain the protocol here, but you can find more information online ([miauth](https://github.com/dnandha/miauth/tree/main/doc) and [NinebotCrypto](https://github.com/scooterhacking/NinebotCrypto)).

To get the authentication token, run the `register` code and pass the scooter MAC to it. The registration token will automatically be saved to a `.mi-token` file. Save that file, you will need it later on.

A pre-compiled version of the `register` is available in the releases section (either for x86_64 and ARM64). You can compile/run the code yourself:

```bash
cargo run --example register 00:1A:2B:3C:4D:5E
```

While running the `register` code, the scooter will beep, meaning that you are trying to log in. **When you hear the beep, touch the power button once to confirm the connection.** This only needs to be done the first time you connect to the scooter.

### Configuring the client

The `m365` clients uses a `martinete.toml` configuration file to adjust the following parameters:
- MQTT broker connection details.
- MQTT client settings (reconnection interval, maximun reconnection interval).
- Client data send frecuency.
- Scooter MAC and `.mi-token` file location.
- GPS serial port connection parameters.

### Running the client

Before running the client ensure you have the following things:

- The server is deployed and ready to accept connections. If not, follow the [server setup instructions here](../server/README.md).
- The `m365` executable is ready.
- The scooter's MAC address.
- All the required parameters are filled out in the [martinete.toml](./../client/martinete.toml) file.

Once everything is ready, put the following files in the same directory:

- The `m365` executable.
- The `martinete.toml` file.
- The `.mi-token`file.

The, run the executable:
```bash
./m365
```

If everything works correctly, you should start seeing data on the MQTT broker after a few seconds. If you have issues, feel free to open an issue on the repository with the error message you get, and I will help you.

**🔔 Note:** Running the executable manually is only for testing purposes. In "production", the client will be started by `systemd`. Continue reading the [Raspberry installation guide](./../raspberry/README.md) for further installation steps.
