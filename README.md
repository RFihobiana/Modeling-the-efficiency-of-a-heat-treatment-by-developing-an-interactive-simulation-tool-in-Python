# Modeling-the-efficiency-of-a-heat-treatment-by-developing-an-interactive-simulation-tool-in-Python
Implementation of the laws of microbial destruction in a graphical interface allowing visualization of the impact of the time/temperature pair on the inactivation of a target pathogen.

## Run

Create a virtual environment, install dependencies and run the Streamlit app:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit (usually http://localhost:8501) to interact with the simulator.

## Quick guide for everyone

This tool helps you explore how heating (time + temperature) reduces microorganisms in food. It's designed so non-experts can try simple scenarios and understand outputs.

- **Initial microbes (per serving)**: an approximate starting count of microbes before heating. If you don't know, leave the default.
- **Temperature** and **Heating time**: pick values you would use when cooking. Higher temperature or longer time removes more microbes.
- **Estimated survivors after heating**: how many microbes may remain after the treatment.
- **Reduction (log10)**: each "log" is a 10× reduction. Examples:
	- 1-log = 90% reduced
	- 2-log = 99% reduced
	- 5-log = 99.999% reduced

Use the presets for simple everyday choices (Gentle, Conservative, Strict). Advanced users can open "Advanced settings" in the sidebar to enter D/z technical parameters.


