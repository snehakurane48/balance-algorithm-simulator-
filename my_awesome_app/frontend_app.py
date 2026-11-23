import os
from pathlib import Path

import pandas as pd
import streamlit as st

from robustness_dashboard import select_run_group, robustness_dashboard_multi


@st.cache_data
def list_runs(results_dir: str = "results"):
    if not os.path.exists(results_dir):
        return []
    runs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
    runs = sorted(runs, reverse=True)
    return runs


@st.cache_data
def load_csv(path: str):
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def show_run(run_name: str):
    base = Path("results") / run_name
    st.header(f"Run: {run_name}")

    plots_dir = base / "plots"
    if not plots_dir.exists():
        st.warning("No plots directory found for this run.")
        return

    st.subheader("Plots")
    pngs = sorted(plots_dir.glob("*.png"))
    if pngs:
        for p in pngs:
            st.image(str(p), caption=p.name)
    else:
        st.info("No PNG plots found in the run's plots folder.")

    st.subheader("Metrics CSVs")
    asr_csv = None
    metrics_csv = None
    for f in base.glob("*.csv"):
        if f.name.startswith("asr_per_client_"):
            asr_csv = f
        if f.name.startswith("metrics_"):
            metrics_csv = f

    if asr_csv and asr_csv.exists():
        st.markdown("**ASR per-client CSV**")
        df = load_csv(str(asr_csv))
        if df is not None:
            st.dataframe(df)
        else:
            st.write("Could not read ASR CSV")
    else:
        st.write("No ASR CSV found for this run.")

    if metrics_csv and metrics_csv.exists():
        st.markdown("**Metrics CSV**")
        dfm = load_csv(str(metrics_csv))
        if dfm is not None:
            st.dataframe(dfm)
        else:
            st.write("Could not read metrics CSV")
    else:
        st.write("No metrics CSV found for this run.")

    st.markdown("---")
    if st.button("Open run folder in file browser"):
        st.write(f"Run folder: {base}")


def generate_combined_dashboard():
    run_group = select_run_group(("results", "my_awesome_app/results"))
    if not run_group:
        st.warning("No compatible runs found under the available result folders. Run some simulations first.")
        return None
    st.info(f"Generating combined dashboard for {len(run_group)} compatible runs")

    import robustness_dashboard as rb

    # Prevent the dashboard from trying to auto-open files on the host
    try:
        rb.open_file = lambda path: None
    except Exception:
        pass

    robustness_dashboard_multi(run_group)
    out_dir = Path(__file__).resolve().parent.parent / "plots"
    out_pdf = out_dir / "robustness_dashboard_combined.pdf"
    out_png = out_dir / "robustness_dashboard_combined.png"
    return out_pdf if out_pdf.exists() else out_png if out_png.exists() else None


def main():
    st.title("BALANCE — Results Dashboard")

    runs = list_runs()
    if not runs:
        st.warning("No result runs found under the `results/` folder. Run simulations first.")
        return

    st.sidebar.title("Available runs")
    selected = st.sidebar.selectbox("Select a run", runs)

    st.sidebar.markdown("---")
    if st.sidebar.button("Generate combined dashboard (latest group)"):
        out = generate_combined_dashboard()
        if out:
            st.success(f"Dashboard created: {out}")
            st.write(f"Download: `{out}`")
        else:
            st.error("Dashboard generation failed or file not found.")

    show_run(selected)


if __name__ == "__main__":
    main()
