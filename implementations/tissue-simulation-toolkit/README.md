# PersistentCell - Model000

This project runs Model000 of the OpenVT persistent random walk project using the [Tissue Simulation Toolkit (TST)](https://github.com/mathbioleiden/Tissue-Simulation-Toolkit). 

---

## 🔬 Model: `model000`

The `model000` example implements a basic random walker using CPM. It runs on the TST backend and is designed for both interactive use and headless batch execution (e.g., on clusters).

---

## 🚀 Getting Started

### 1. Clone and Build the Tissue Simulation Toolkit

To use this project, you first need to clone and build the custom `OpenVT` branch of the Tissue Simulation Toolkit:

```bash
git clone --branch OpenVT https://github.com/mathbioleiden/Tissue-Simulation-Toolkit.git
cd Tissue-Simulation-Toolkit
mkdir build && cd build
cmake ..
make
```

This builds the required simulation backends, including `openvt-persistentrandomwalk-model000-tst`.

---

## ▶️ Run the Model

This repository includes a Python script to run multiple simulations using the `model000` setup.

From the root of the `PersistentCell` repository:

```bash
cd openvt
python3 modelrun000.py
```

The script will:

- Load `input.json` to read the number of simulations (`num_sims`)
- Launch the `openvt-persistentrandomwalk-model000-tst` executable with incrementing simulation IDs
- Optionally append `-platform offscreen` to run headlessly

---

## 💻 Running on a Cluster (Headless Mode)

To prevent graphical windows from opening (e.g., on an HPC cluster), use the following command-line option when launching the TST executable:

```bash
-platform offscreen
```

Example:

```bash
./openvt-persistentrandomwalk-model000-tst -platform offscreen dummy 0
```

You can modify `modelrun000.py` to include this flag if needed for batch jobs.

---

## 📁 Directory Structure

```
PersistentCell/
├── openvt/
│   ├── config.json         # Simulation parameters
│   ├── modelrun000.py      # Python launcher for simulations
│   └── (outputs, logs, .csv files)
```

---

## 🧠 Requirements

- **Compiler:** C++17 compatible (e.g., g++ ≥ 7, clang ≥ 6)
- **Build system:** CMake ≥ 3.10
- **Python:** 3.6 or higher
- **Qt:** Qt5 or Qt6 (with `offscreen` platform plugin for headless runs)

Optional (for development and testing):
- Jupyter Notebook (for visualization/analysis)
- matplotlib, numpy

---


## 📫 Contact

For bug reports, feature requests, or questions, please open an issue or contact the authors via the [Tissue Simulation Toolkit GitHub page](https://github.com/mathbioleiden/Tissue-Simulation-Toolkit).
