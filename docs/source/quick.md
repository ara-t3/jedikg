# Quick Start Guide


## Software Requirements 

Before using this project, ensure the following software is installed:

```{tip}
It is highly recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage Python versions. This allows easy switching between versions and avoids system conflicts.
```

1. **Ubuntu 20** or later. The project has been developed on Linux Ubuntu System. Compatibility with other systems has not been tested.

1. **Python 3.9** or later. If you already have Python 3.9+ installed system-wide, pyenv is optional but recommended.

2. **Java 8** or later. This is needed only if you plan to use Justification tools, due to *Pellet* dependecies.

2. **Java 11** or later. This is need by the *Robot OBO Utility* backbone of the reasoning services.



## Installation Instructions

1. **Clone** the repository

```bash
git clone https://github.com/ivandiliso/kg-saf.git
cd kg-saf
```

2. **Install** Python dependencies

```bash
pip install -r requirements.txt
```

3. **Verify** requirements are installed

```bash
python --version
java -version
java -jar robot.jar --help
```

## System Requirements

```{warning}
Running this project with less than 8 GB of RAM may cause crashes or slow performance.
```

- Memory: 8 GB minimum (16GB reccomended for reasoning services)
- Disk Space: 15 GB for dataset and ontologies


## Unpack Released Datasets

```{warning}
```

The released datasets and ontologies are distributed in **compressed ZIP files** due to GitHub storage limitations. Some secondary files were removed to reduce size, but they **can be reconstructed** using the provided unpacking utility. 


1. Open the provided **dataset unpacking notebook** (`kgsaf_jdex/utils/unpack.ipynb`).  
2. Execute **all cells sequentially**.  
3. The notebook will automatically perform the following steps:
    - **Unpack all compressed datasets and ontologies** into an `kgsaf_data/datasets/*/unpack` and `kgsaf_data/ontologies/*/unpack`folder.  
    - **Re-merge object property assertion files** for each dataset.  
    - **Merge the full knowledge graph** (TBox, RBox, and ABox) using a reasoner (Robot OBO Tool).  
    - **Convert N-Triples files to TSV format**, ready for use with ML libraries such as **PyKEEN**.  
    - **Convert Schema files to JSON** (taxonomy, roles, class assertions) for easier loading and manipulation in Python.

