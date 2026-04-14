# Quick Start Guide


## Software Requirements 

Before using this project, ensure the following software is installed:

```{tip}
It is highly recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage Python versions. This allows easy switching between versions and avoids system conflicts.
```

1. **Ubuntu 20** or later. The project has been developed on Linux Ubuntu System. Compatibility with other systems has not been tested.

1. **Python >=3.11** or later. If you already have Python >=3.11 installed system-wide, pyenv is optional but recommended.

2. **Java 8** or later. This is needed only if you plan to use Justification tools, due to *Pellet* dependecies.

2. **Java 11** or later. This is need by the *Robot OBO Utility* backbone of the reasoning services.

## System Requirements

```{warning}
Running this project with less than 8 GB of RAM may cause crashes or slow performance.
```

- Memory: 8 GB minimum (16GB reccomended for reasoning services)
- Disk Space: 15 GB for dataset and ontologies


## Installation Instructions

1. **Clone** the repository

```bash
git clone https://github.com/ivandiliso/kg-saf.git
cd kg-saf
```

2. Run the **Automatic Interactive Installer**

```bash
chmod +x install
./install
```

Follow the instruction provided via terminal to customize you installation.

```{warning}
The KG-SaF Dataset are provided in a zipped and stripped down version due to GitHub cloud per file size limitation, do to this, full knowledge graph and full assertions files have been removed, but can be easily reconstructed using the provided installation options. Please refer to the installation instruction and process to automatically unpack all resources and reconstruc all removed files.
```

```{tip}
If you just want to use the JDEX utility on your custom dataset and are not interested in the KG-SaF Data Consistent Dataset, choose "No" when prompted about running dataset unpacking. THe JDEX tool can be used also whitout data!
```

## Run JDEX on your Knowledge Graph

To run JDEX, you only need a properly defined configuration file. Once that’s ready, launch the CLI interactive interface with:

```bash
chmod +x run_jdex
./run_jdex --config "path_to_your_json.json"
```

This command will handle the entire pipeline for you — including all utilities, processing steps, and detailed logging.
The only requirement is a well-defined configuration file. For guidance, refer to **"JDEX Configuration Guide"**.

### Minimal Required Inputs
- **Schema file**: your ontology schema
- **Facts file**: your triples, including object property assertions and class assertions


