import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Page config
st.set_page_config(page_title="Virtual lab for simulating P chart", layout="wide")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = 1

SPHERE_IMG = "sphere.png"
SNAP_GAUGE_IMG = "snap_gauge_image.jpeg"

# ------------------------ SECTION 1 ------------------------ #
if st.session_state.page == 1:
    st.title("🔧 Virtual lab for simulating P chart")

    with st.expander("📖 Introduction", expanded=True):
        st.markdown("""
        <div style='font-size:18px; text-align: justify;'>
        The <b>Virtual Lab for Simulating P Chart</b> offers an interactive environment to understand quality control in manufacturing processes using Snap Gauges and P Charts. Snap Gauges are essential inspection tools used to quickly assess whether components meet dimensional specifications, classifying them as ‘Go’ or ‘No Go’ based on tolerance limits.
        <br><br>
        In this virtual lab, users can simulate the inspection of spherical components by specifying the number of batches, sample size, and dimensional parameters of the gauge and spheres. Each sphere is inspected interactively, and its conformity is determined using defined gauge limits. Once all batches are tested, the lab generates a P Chart that displays the proportion of defective items per batch. A summary table is also provided, detailing batch-wise inspection results.
        <br><br>
        This lab serves as an educational tool to help users visualize and analyze attribute-based quality control, statistical process behavior, and the application of control charts in real-world scenarios.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🎯 Objective and Procedure", expanded=True):
        st.markdown("""
        <div style='font-size:18px; text-align: justify;'>
        <b>🎯 Objective:</b><br>
        Simulate inspection of spheres using a virtual Snap Gauge and analyze quality through batch-wise testing and P Chart.
        <br><br>
        <b>🧪 Procedure:</b><br>
        1. Enter number of batches, samples per batch, and dimensional parameters.<br>
        2. Click 'Check' under each sphere to test it inside the Snap Gauge.<br>
        3. Only accepted spheres within <b>Gauge Diameter ± Tolerance</b> are marked <b>Go</b>, else <b>No Go</b>.<br>
        4. Complete each batch before moving to the next.<br>
        5. View <b>P Chart</b> after all batches are done.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📚 Learning Outcomes"):
        st.markdown("""
        <div style='font-size:18px; text-align: justify;'>
        By the end of this virtual lab, you will be able to:<br>
        • Understand how Snap Gauges are used in dimensional quality control.<br>
        • Identify conforming and non-conforming parts using inspection logic.<br>
        • Monitor batch-wise defect proportions using a P Chart.<br>
        • Interpret process stability using control limits.<br>
        • Apply quality control concepts to simulated real-world scenarios.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📘 Glossary of Terms"):
        st.markdown("""
        <div style='font-size:18px; text-align: justify;'>
        <b>Snap Gauge:</b> A fixed-limit tool used to inspect whether a part's diameter is within tolerance.<br><br>
        <b>Go/No Go:</b> Terminology used to determine whether a part passes (Go) or fails (No Go) inspection.<br><br>
        <b>Tolerance:</b> The permissible limit or limits of variation in a physical dimension.<br><br>
        <b>Defective Unit:</b> A component that does not meet the required specifications.<br><br>
        <b>P Chart:</b> A control chart used to monitor the proportion of defective items in a process.<br><br>
        <b>Control Limits:</b> The upper and lower statistical boundaries used to determine if a process is in control.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("ℹ️ About Snap Gauges and P Charts"):
        st.markdown("""
        <div style='font-size:18px; text-align: justify;'>
        A <i>P chart</i> (proportion chart) in quality control is used to monitor the proportion of defective items in a process over time, particularly for attributes data where each unit is classified as either defective or non-defective. It helps identify variations due to assignable causes and ensure the process remains within control limits.
        <br><br>
        On the other hand, a <i>snap gauge</i> is a fixed-limit gauge commonly used for quick and accurate inspection of diameters, especially in high-volume production. It provides a go/no-go decision by allowing or rejecting parts based on whether they fall within the specified dimensional tolerances, making it an efficient tool for checking external diameters without requiring precise readings.
        </div>
        """, unsafe_allow_html=True)

    # Add Snap Gauge and P Chart Images with reduced size
    st.markdown("### 📷 Snap Gauge")
    st.image("snap_gauge_image.jpeg", caption="Example of a Snap Gauge", width=400)

    st.markdown("### 📊 Example P Chart")
    st.image("p_chart_example.png", caption="Example of a P Chart", width=400)

    if st.button("Next"):
        st.session_state.page = 2

# ------------------------ SECTION 2 ------------------------ #
elif st.session_state.page == 2:
    st.title("🔧 Input Parameters")
    st.markdown("### Please input the following parameters:")

    with st.form("input_form"):
        input_batches = st.number_input("No. of Samples:", min_value=1, value=5)
        input_samples = st.number_input("Sample Size:", min_value=1, value=5)
        input_snap_diameter = st.number_input("Diameter of Snap Gauge (mm):", min_value=1.0, value=50.0)
        input_snap_tolerance = st.number_input("Tolerance of Snap Gauge (mm):", min_value=0.01, value=0.5)
        input_sphere_diameter = st.number_input("Nominal Diameter of Sphere (mm):", min_value=1.0, value=50.0)
        submitted = st.form_submit_button("Next")

    if submitted:
        st.session_state.no_of_batches = input_batches
        st.session_state.no_of_samples_per_batch = input_samples
        st.session_state.snap_diameter = input_snap_diameter
        st.session_state.snap_tolerance = input_snap_tolerance
        st.session_state.sphere_diameter = input_sphere_diameter

        st.session_state.spheres = [
            round(random.uniform(input_sphere_diameter - 1.0, input_sphere_diameter + 1.0), 2)
            for _ in range(input_batches * input_samples)
        ]

        st.session_state.selected = []
        st.session_state.batches = []
        st.session_state.completed_batches = 0
        st.session_state.page = 3

# ------------------------ SECTION 3 ------------------------ #
elif st.session_state.page == 3:
    st.title("🔧 Sphere Inspection and P Chart Generation")

    no_of_batches = st.session_state.no_of_batches
    no_of_samples_per_batch = st.session_state.no_of_samples_per_batch
    snap_diameter = st.session_state.snap_diameter
    snap_tolerance = st.session_state.snap_tolerance
    LCL = snap_diameter - snap_tolerance
    UCL = snap_diameter + snap_tolerance

    st.markdown(f"**Snap Gauge Range**: {snap_diameter} ± {snap_tolerance} mm → [{LCL}, {UCL}] mm")

    if "batch_spheres" not in st.session_state:
        st.session_state.batch_spheres = [
            [round(random.uniform(st.session_state.sphere_diameter - 1.0,
                                  st.session_state.sphere_diameter + 1.0), 2)
             for _ in range(no_of_samples_per_batch)]
            for _ in range(no_of_batches)
        ]
        st.session_state.batch_results = [[] for _ in range(no_of_batches)]

    all_done = True

    for batch_index in range(no_of_batches):
        st.markdown(f"### 🧪 Batch {batch_index + 1}")

        if f"remaining_batch_{batch_index}" not in st.session_state:
            st.session_state[f"remaining_batch_{batch_index}"] = st.session_state.batch_spheres[batch_index][:]

        if len(st.session_state.batch_results[batch_index]) < no_of_samples_per_batch:
            all_done = False
            cols = st.columns(5)
            updated_batch = []

            for i, diameter in enumerate(st.session_state[f"remaining_batch_{batch_index}"]):
                col = cols[i % 5]
                col.image(SPHERE_IMG, width=50)
                col.markdown(f"**{diameter} mm**")
                if col.button("Check", key=f"check_button_{batch_index}_{i}"):
                    result = "Go" if LCL <= diameter <= UCL else "No Go"
                    st.session_state.batch_results[batch_index].append((diameter, result))
                else:
                    updated_batch.append(diameter)

            st.session_state[f"remaining_batch_{batch_index}"] = updated_batch

            if st.session_state.batch_results[batch_index]:
                st.markdown("**Current Batch Results:**")
                for i, (d, r) in enumerate(st.session_state.batch_results[batch_index]):
                    st.markdown(f"- **Sphere {i+1}**: {d} mm → {r}")

            st.markdown("---")

    if all_done:
        st.subheader("📈 Final P Chart and Summary Table")

        proportions = []
        summary_data = []

        for i, batch in enumerate(st.session_state.batch_results):
            n_total = len(batch)
            n_defective = sum(1 for _, result in batch if result == "No Go")
            p = n_defective / n_total if n_total > 0 else 0
            proportions.append(p)

            summary_data.append({
                "S. No.": i + 1,
                "No. of components inspected": n_total,
                "No. of defective components": n_defective,
                "Defective Ratio": round(p, 3)
            })

        # Correct control limits
        total_defectives = sum(x["No. of defective components"] for x in summary_data)
        total_inspected = sum(x["No. of components inspected"] for x in summary_data)
        avg_p = total_defectives / total_inspected
        std_err = np.sqrt((avg_p * (1 - avg_p)) / no_of_samples_per_batch)
        ucl = avg_p + 3 * std_err
        lcl = max(0, avg_p - 3 * std_err)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(proportions, marker='o', linestyle='-', color='blue', label="P Chart")
        ax.axhline(y=avg_p, color='red', linestyle='dashed', label="CL")
        ax.axhline(y=ucl, color='green', linestyle='dashed', label="UCL")
        ax.axhline(y=lcl, color='green', linestyle='dashed', label="LCL")

        max_defects = max(summary_data, key=lambda x: x["No. of defective components"])
        max_index = max_defects["S. No."] - 1
        ax.annotate(f"Most Defectives: {max_defects['No. of defective components']}",
                    (max_index, proportions[max_index]),
                    textcoords="offset points", xytext=(0, 10), ha='center', color='red')

        ax.set_title("P-Chart")
        ax.set_xlabel("Batch Number")
        ax.set_ylabel("Defective Proportion")
        ax.legend()
        st.pyplot(fig)

        st.subheader("📋 Summary Table")
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        st.subheader("📊 Inference")
        out_of_control = any(p > ucl or p < lcl for p in proportions)
        if out_of_control:
            st.error("❌ One or more points fall outside the control limits — process is OUT OF CONTROL (assignable causes present).")
        elif avg_p in [0.0, 1.0]:
            st.warning("⚠️ All results are identical (all 'Go' or all 'No Go') — no variation detected, possible data or process issue.")
        else:
            st.success("✅ All points within control limits — process is in control.")

    st.markdown("---")
    if st.button("🔁 Restart Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
