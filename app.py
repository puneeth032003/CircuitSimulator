import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import re
import cmath
import math

def parse_value(val_str):
    """Convert a value string to a number or complex number (for AC)."""
    if "∠" in val_str:
        mag, ang = val_str.split("∠")
        mag = float(mag)
        ang = float(ang)
        ang_rad = math.radians(ang)
        return cmath.rect(mag, ang_rad)
    else:
        return float(val_str)


# -------------------------
# Parse circuit file
# -------------------------
def parse_circuit_file(file_content, mode="DC"):
    resistors, voltage_sources = [], []
    for line in file_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        name = parts[0]
        n1, n2 = int(parts[1]), int(parts[2])
        val_str = parts[3]

        if mode == "AC":
            # Expect AC voltages in phasor form: 10∠30 or 5∠-45
            match = re.match(r"([0-9.]+)∠([-+]?[0-9.]+)", val_str)
            if match:
                magnitude = float(match.group(1))
                phase_deg = float(match.group(2))
                val = magnitude * np.exp(1j * np.deg2rad(phase_deg))
            else:
                val = float(val_str)
        else:
            val = float(val_str)

        if name[0].upper() == "R":
            resistors.append((name, n1, n2, val))
        elif name[0].upper() == "V":
            voltage_sources.append((name, n1, n2, val))
    return resistors, voltage_sources

# -------------------------
# Simulation function
# -------------------------
def simulate_circuit(file_content, mode="DC"):
    resistors, voltage_sources = parse_circuit_file(file_content, mode)
    num_nodes = max(max(n1, n2) for _, n1, n2, _ in resistors + voltage_sources)
    num_vsources = len(voltage_sources)

    dtype = np.complex128 if mode=="AC" else np.float64

    G = np.zeros((num_nodes, num_nodes), dtype=dtype)
    B = np.zeros((num_nodes, num_vsources), dtype=dtype)
    z = np.zeros((num_nodes + num_vsources, 1), dtype=dtype)

    # Fill G matrix for resistors
    for _, n1, n2, val in resistors:
        g = 1 / val
        if n1 != 0: G[n1-1, n1-1] += g
        if n2 != 0: G[n2-1, n2-1] += g
        if n1 != 0 and n2 != 0:
            G[n1-1, n2-1] -= g
            G[n2-1, n1-1] -= g

    # Fill B matrix for voltage sources
    for k, (_, n1, n2, val) in enumerate(voltage_sources):
        if n1 != 0: B[n1-1, k] = 1
        if n2 != 0: B[n2-1, k] = -1
        z[num_nodes + k, 0] = val

    # Solve MNA equations
    C = B.T
    D = np.zeros((num_vsources, num_vsources), dtype=dtype)
    A = np.block([[G, B], [C, D]])

    try:
        x = np.linalg.solve(A, z)
    except np.linalg.LinAlgError:
        return "❌ Circuit cannot be solved (singular matrix). Check connections."

    voltages = x[:num_nodes]
    source_currents = x[num_nodes:]

    # -------------------------
    # Prepare result text
    # -------------------------
    result = f"Simulation Mode: {mode}\n\n"
    result += "Node Voltages:\n"
    for i, v in enumerate(voltages, 1):
        if mode=="AC":
            mag, phase = np.abs(v.item()), np.angle(v.item(), deg=True)
            result += f"  V({i}) = {mag:.4f}∠{phase:.2f}° V\n"
        else:
            result += f"  V({i}) = {v.item():.4f} V\n"

    result += "\nVoltage Source Currents:\n"
    for i, i_s in enumerate(source_currents, 1):
        if mode=="AC":
            mag, phase = np.abs(i_s.item()), np.angle(i_s.item(), deg=True)
            result += f"  I(V{i}) = {mag:.6f}∠{phase:.2f}° A\n"
        else:
            result += f"  I(V{i}) = {i_s.item():.6f} A\n"

    result += "\nResistor Currents:\n"
    for name, n1, n2, val in resistors:
        v1 = voltages[n1-1].item() if n1 != 0 else 0
        v2 = voltages[n2-1].item() if n2 != 0 else 0
        current = (v1 - v2) / val
        if mode=="AC":
            mag, phase = np.abs(current), np.angle(current, deg=True)
            result += f"  I({name}) = {mag:.6f}∠{phase:.2f}° A (from node {n1} to {n2})\n"
        else:
            result += f"  I({name}) = {current:.6f} A (from node {n1} to {n2})\n"

    # -------------------------
    # Visualization
    # -------------------------
    st.subheader("🔹 Circuit Visualization")
    G_draw = nx.Graph()
    all_nodes = set()
    for _, n1, n2, _ in resistors + voltage_sources:
        all_nodes.update([n1, n2])
    for node in all_nodes:
        G_draw.add_node(str(node))
    for i, (name, n1, n2, val) in enumerate(resistors, 1):
        G_draw.add_edge(str(n1), str(n2), label=f"{name}\n{val}Ω")
    for i, (name, n1, n2, val) in enumerate(voltage_sources, 1):
        G_draw.add_edge(str(n1), str(n2), label=f"{name}\n{val}V")
    pos = nx.spring_layout(G_draw, seed=42)
    plt.figure(figsize=(6, 4))
    nx.draw(G_draw, pos, with_labels=True, node_color="lightblue", node_size=800, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G_draw, "label")
    nx.draw_networkx_edge_labels(G_draw, pos, edge_labels=edge_labels, font_size=8)
    st.pyplot(plt)

    return result

# -------------------------
# Streamlit UI
# -------------------------
st.title("⚡ AC/DC Circuit Simulator (Phasor Support)")

mode = st.radio("Select Simulation Type:", ["DC", "AC"])
st.markdown("**AC voltages should be in phasor format:** e.g., `10∠30` for 10V with 30° phase.")

uploaded_file = st.file_uploader("Upload your circuit file (.txt)", type=["txt"])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.text_area("Circuit Definition", content, height=150)
    if st.button("Simulate"):
        try:
            output = simulate_circuit(content, mode)
            st.text_area("Simulation Output", output, height=400)
        except Exception as e:
            st.error(f"Error: {e}")
