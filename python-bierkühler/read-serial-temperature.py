import serial
import time
import re
import sys
import matplotlib.pyplot as plt

# --- KONFIGURATION ---
# Trage hier deinen Port ein:
# Windows z.B.: 'COM3' oder 'COM4'
# Linux z.B.: '/dev/ttyUSB0'
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

def main():
    try:
        # Verbinde mit dem seriellen Port
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Erfolgreich verbunden mit {PORT} bei {BAUDRATE} Baud.")
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports {PORT}. Läuft noch ein anderes Programm (z.B. tio/screen)?")
        print(f"Details: {e}")
        sys.exit(1)

    print("Warte auf 'MARKER: START' (Drücke den Knopf an deinem STM32)...")

    recording = False
    times = []
    temps = []
    start_time = None

    try:
        while True:
            # Lese eine Zeile vom seriellen Port
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                print(f"STM32: {line}")

                # === START-SIGNAL PRÜFEN ===
                if "MARKER: START" in line:
                    print("--> Start-Signal erkannt! Zeichne ab jetzt Daten auf...")
                    recording = True
                    times = []       # Listen leeren für neue Messung
                    temps = []
                    start_time = time.time()
                    continue

                # === STOP-SIGNAL PRÜFEN ===
                if "MARKER: STOP" in line:
                    if recording:
                        print("--> Stop-Signal erkannt! Beende Aufzeichnung und generiere Graph...")
                        recording = False
                        break # Verlasse die Endlosschleife, um den Plot zu zeichnen
                    else:
                        print("--> Stop-Signal ignoriert (System war nicht im Aufzeichnungs-Modus).")

                # === TEMPERATUR AUSLESEN ===
                if recording and "Bier-Temperatur:" in line:
                    # Wir nutzen Regex, um die Kommazahl aus dem Text zu filtern (auch mit Minuszeichen)
                    match = re.search(r"Bier-Temperatur:\s*(-?\d+\.\d+)", line)
                    if match:
                        temp_val = float(match.group(1))
                        # Berechne vergangene Sekunden seit dem Start
                        elapsed_time = time.time() - start_time

                        times.append(elapsed_time)
                        temps.append(temp_val)

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer (Strg+C) abgebrochen.")
    finally:
        ser.close()
        print("Serieller Port geschlossen.")

    # === DATEN PLOTTEN ===
    if len(times) > 0 and len(temps) > 0:
        print(f"Generiere Kurve aus {len(temps)} Messpunkten...")

        plt.figure(figsize=(10, 6))

        # Erstelle die Linie mit Punkten
        plt.plot(times, temps, marker='o', linestyle='-', color='b', label='Bier-Temperatur')

        # Design & Beschriftungen
        plt.title("Bier-Temperatur Messkurve", fontsize=16)
        plt.xlabel("Zeit seit Messbeginn (Sekunden)", fontsize=12)
        plt.ylabel("Temperatur (°C)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()

        # Zeige das interaktive Fenster an
        plt.show()
    else:
        print("Es wurden keine Temperaturdaten gesammelt, die gezeichnet werden könnten.")

if __name__ == '__main__':
    main()
