# ⚡ Circuit Simulator (AC & DC)

A **Python-based circuit simulator** built using **Streamlit** for visualizing and analyzing **both AC and DC circuits**.  
This project allows users to simulate voltage, current, and resistor behavior for custom circuits defined in `.txt` files.

---

## 🔹 Features

- Supports **DC and AC voltage sources**.
- Automatically computes:
  - Node voltages
  - Voltage source currents
  - Resistor currents
- Visualizes circuit topology using **network graphs**.
- Handles complex AC sources using **phasors (magnitude ∠ phase)**.
- Supports multiple test circuits for quick evaluation.
- Lightweight and interactive **web interface** with Streamlit.

---

## 📂 Project Structure
CircuitSimulator/
│
├── app.py # Main Streamlit application
├── test_circuits/ # Folder containing AC/DC test circuit files
│ ├── dc_test1.txt
│ ├── dc_test2.txt
│ ├── ac_test1.txt
│ └── ac_test2.txt
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── .gitignore # Ignored files/folders

---

## 📝 Circuit File Format

Each circuit file is a plain text file with the following format:

Resistors: R<name> <node1> <node2> <value in Ohms>
DC Voltage Sources: V<name> <node1> <node2> <value in Volts>
AC Voltage Sources: V<name> <node1> <node2> <value∠phase in Volts>

Example (DC):
V1 1 0 10
R1 1 2 1000
R2 2 0 2000

Example (AC):
V1 1 0 15∠45
R1 1 2 1000
R2 2 0 2000


> **Note:** For AC sources, use the format `magnitude∠phase` (e.g., `15∠30`) to represent phasor voltage.

---

## 🚀 Installation

## 1. Clone the repository:
git clone https://github.com/puneeth032003/CircuitSimulator.git
cd CircuitSimulator
## 2. Install required packages:
   pip install -r requirements.txt
## 3. 🖥 Running the Simulator
   streamlit run app.py

Upload a .txt circuit file (AC or DC).
Click Simulate.
View node voltages, current through sources, resistor currents, and circuit visualization.

## 📈 Future Enhancements

Add support for capacitors and inductors.
Frequency-domain AC analysis (phasor diagrams).
Export simulation results to CSV or PDF.
Interactive drag-and-drop circuit builder.

## 🛠 Tech Stack

Python 3.10+
Streamlit – Web-based UI
NumPy – Numerical computation
NetworkX & Matplotlib – Circuit visualization
