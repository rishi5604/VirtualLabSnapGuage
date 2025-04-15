import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Page config
st.set_page_config(page_title="Virtual Snap Gauge Simulator", layout="wide")
st.title("🔧 Virtual Snap Gauge Simulator")

# Constants
NOMINAL = 50
TOLERANCE = 0.5
UCL = NOMINAL + TOLERANCE
LCL = NOMINAL - TOLERANCE

# Load images
SPHERE_IMG = "sphere.png"  # Ensure this is a PNG with transparency
SNAP_GAUGE_IMG = "snap_gauge_image.jpeg"

# Initialize session state
if "spheres" not in st.session_state:
    st.session_state.spheres = [round(random.uniform(49.3, 50.7), 2) for _ in range(15)]
    st.session_state.selected_sphere_index = None
    st.session_state.selected = []
    st.session_state.batches = []

# Layout: Use a fixed left column for the Snap Gauge image
col1, col2 = st.columns([1, 5])  # First column for Snap Gauge, second for spheres and results

# Snap Gauge Image always visible in the first column
with col1:
    st.image(SNAP_GAUGE_IMG, width=150)
    st.markdown(f"**Snap Gauge Range**: {NOMINAL} ± {TOLERANCE} mm → [{LCL}, {UCL}] mm")

# Sphere Interaction and Drop Zone in the second column
with col2:
    st.markdown("### 🟢 Click a sphere, then place it inside the Snap Gauge box below")

    # Sphere Display
    cols = st.columns(5)
    for i, diameter in enumerate(st.session_state.spheres):
        col = cols[i % 5]
        
        # Create a button for each sphere with the sphere's diameter
        if col.button(f"{diameter} mm", key=f"sphere_button_{i}"):
            st.session_state.selected_sphere_index = i  # Track the selected sphere's index

        # Display the sphere image without the diameter caption
        col.image(SPHERE_IMG, width=50, use_container_width=False)

    # Snap Gauge "Drop Zone"
    st.markdown("---")
    st.subheader("⬇️ Drop Zone: Snap Gauge")

    # Create a row with the Snap Gauge image and the button beside it
    button_col1, button_col2 = st.columns([4, 1])  # First for image, second for button

    with button_col1:
        st.image(SNAP_GAUGE_IMG, width=150)  # Place the Snap Gauge image beside the button

    with button_col2:
        # Check if a sphere is selected
        if st.session_state.selected_sphere_index is not None:
            if st.button("Place Sphere Inside Snap Gauge"):
                index = st.session_state.selected_sphere_index
                diameter = st.session_state.spheres[index]
                result = "Go" if LCL <= diameter <= UCL else "No Go"
                st.session_state.selected.append((diameter, result))
                del st.session_state.spheres[index]
                st.session_state.selected_sphere_index = None

    # Show current batch test results
    if st.session_state.selected:
        st.subheader("📋 Current Batch Results")
        for i, (d, r) in enumerate(st.session_state.selected):
            st.markdown(f"- **Sphere {i+1}**: {d} mm → `{r}`")

    # Batch completion and analysis
    if len(st.session_state.selected) == 5:
        st.success("✅ Batch complete!")
        st.session_state.batches.append(st.session_state.selected)
        st.session_state.selected = []

    # Generate P Chart
    if len(st.session_state.batches) == 3:
        st.subheader("📈 P Chart")

        batch_sizes = [len(batch) for batch in st.session_state.batches]
        defective_counts = [sum(1 for _, result in batch if result == "No Go") for batch in st.session_state.batches]
        proportions = [defective / size for defective, size in zip(defective_counts, batch_sizes)]

        avg_p = np.mean(proportions)
        ucl = avg_p + 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes))
        lcl = max(0, avg_p - 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes)))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(proportions, marker='o', linestyle='-', color='blue', label="P Chart")
        ax.axhline(y=avg_p, color='red', linestyle='dashed', label="CL")
        ax.axhline(y=ucl, color='green', linestyle='dashed', label="UCL")
        ax.axhline(y=lcl, color='green', linestyle='dashed', label="LCL")

        max_defects = max(defective_counts)
        for i, count in enumerate(defective_counts):
            if count == max_defects:
                ax.annotate(f"Most Defectives: {count}", (i, proportions[i]), textcoords="offset points", xytext=(0, 10), ha='center', color='red')

        ax.set_title("P-Chart (Defective Proportion per Batch)")
        ax.set_xlabel("Batch Number")
        ax.set_ylabel("Defective Proportion")
        ax.legend()
        st.pyplot(fig)

        # Save results
        df = pd.DataFrame(
            [(i + 1, diameter, result) for i, batch in enumerate(st.session_state.batches) for (diameter, result) in batch],
            columns=["Batch", "Diameter (mm)", "Result"]
        )
        os.makedirs("results", exist_ok=True)
        excel_path = "results/snap_gauge_results.xlsx"
        csv_path = "results/snap_gauge_results.csv"
        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)

        st.success("✅ Results saved to `results/` folder.")
        st.download_button("📥 Download Excel", data=open(excel_path, "rb"), file_name="snap_gauge_results.xlsx")
        st.download_button("📥 Download CSV", data=open(csv_path, "rb"), file_name="snap_gauge_results.csv")

        # Reset session
        st.session_state.clear()
