import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Page config
st.set_page_config(page_title="Virtual Snap Gauge Simulator", layout="wide")

# Take input from user for number of batches and samples per batch
st.markdown("### Please input the following parameters:")
no_of_batches = st.number_input("No of Batches:", min_value=1, value=5)
no_of_samples_per_batch = st.number_input("No of Samples per Batch:", min_value=1, value=5)

# Display title after inputs
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
    # Update the number of spheres based on the input values
    st.session_state.spheres = [round(random.uniform(49.3, 50.7), 2) for _ in range(no_of_batches * no_of_samples_per_batch)]
    st.session_state.selected_sphere_index = None
    st.session_state.selected = []
    st.session_state.batches = []

if "completed_batches" not in st.session_state:
    st.session_state.completed_batches = 0  # Track the number of completed batches

# Layout: Use a fixed left column for the Snap Gauge image
col1, col2 = st.columns([1, 5])

with col1:
    st.image(SNAP_GAUGE_IMG, width=150)
    st.markdown(f"**Snap Gauge Range**: {NOMINAL} ± {TOLERANCE} mm → [{LCL}, {UCL}] mm")

with col2:
    st.markdown("### 🟢 Click a sphere, then place it inside the Snap Gauge box below")

    cols = st.columns(5)
    for i, diameter in enumerate(st.session_state.spheres):
        col = cols[i % 5]
        if col.button(f"{diameter} mm", key=f"sphere_button_{i}"):
            st.session_state.selected_sphere_index = i
        col.image(SPHERE_IMG, width=50, use_container_width=False)

    st.markdown("---")
    st.subheader("⬇️ Drop Zone: Snap Gauge")

    button_col1, button_col2 = st.columns([4, 1])
    with button_col1:
        st.image(SNAP_GAUGE_IMG, width=150)
    with button_col2:
        if st.session_state.selected_sphere_index is not None:
            if st.session_state.completed_batches < no_of_batches:
                if len(st.session_state.selected) < no_of_samples_per_batch:
                    if st.button("Place Sphere Inside Snap Gauge"):
                        index = st.session_state.selected_sphere_index
                        diameter = st.session_state.spheres[index]
                        result = "Go" if LCL <= diameter <= UCL else "No Go"
                        st.session_state.selected.append((diameter, result))
                        del st.session_state.spheres[index]
                        st.session_state.selected_sphere_index = None
                else:
                    st.warning("Batch Size Exceeded! Please complete the current batch before proceeding.")
            else:
                st.warning("You have already completed the maximum number of batches.")

    # Display current batch results
    if st.session_state.selected:
        st.subheader("📋 Current Batch Results")
        for i, (d, r) in enumerate(st.session_state.selected):
            st.markdown(f"- **Sphere {i+1}**: {d} mm → {r}")

    # Complete batch after filling up to "No of Samples per Batch"
    if len(st.session_state.selected) == no_of_samples_per_batch:
        st.success("✅ Batch complete!")
        st.session_state.batches.append(st.session_state.selected)
        st.session_state.selected = []
        st.session_state.completed_batches += 1

# ✅ Show final results *only after all batches are used*
if st.session_state.completed_batches == no_of_batches:
    st.subheader("📈 Final P Chart and Batch Results")

    # Calculate chart data
    batch_sizes = [len(batch) for batch in st.session_state.batches]
    defective_counts = [sum(1 for _, result in batch if result == "No Go") for batch in st.session_state.batches]
    proportions = [defective / size for defective, size in zip(defective_counts, batch_sizes)]

    avg_p = np.mean(proportions)
    ucl = avg_p + 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes))
    lcl = max(0, avg_p - 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes)))

    # Prepare the chart
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(proportions, marker='o', linestyle='-', color='blue', label="P Chart")
    ax.axhline(y=avg_p, color='red', linestyle='dashed', label="CL")
    ax.axhline(y=ucl, color='green', linestyle='dashed', label="UCL")
    ax.axhline(y=lcl, color='green', linestyle='dashed', label="LCL")

    max_defects = max(defective_counts)
    for i, count in enumerate(defective_counts):
        if count == max_defects:
            ax.annotate(f"Most Defectives: {count}", (i, proportions[i]), textcoords="offset points", xytext=(0, 10), ha='center', color='red')

    ax.set_title("P-Chart")
    ax.set_xlabel("Batch Number")
    ax.set_ylabel("Defective Proportion")
    ax.legend()

    # Side-by-side display
    chart_col, data_col = st.columns(2)

    with chart_col:
        st.pyplot(fig)

    with data_col:
        # Create a dataframe for all batches and their results
        df = pd.DataFrame(
            [(i + 1, diameter, result) for i, batch in enumerate(st.session_state.batches) for (diameter, result) in batch],
            columns=["Batch", "Diameter (mm)", "Result"]
        )
        st.dataframe(df)

        # Save results to files
        os.makedirs("results", exist_ok=True)
        excel_path = "results/snap_gauge_results.xlsx"
        csv_path = "results/snap_gauge_results.csv"
        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)

        st.success("✅ Results saved to results/ folder.")
        st.download_button("📥 Download Excel", data=open(excel_path, "rb"), file_name="snap_gauge_results.xlsx")
        st.download_button("📥 Download CSV", data=open(csv_path, "rb"), file_name="snap_gauge_results.csv")
