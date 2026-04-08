# JDEX Configuration Guide

JDEX is fully configurable through a JSON configuration file. This allows you to control every stage of the pipeline, from reasoning services to dataset splitting and post-processing.
This tutorial walks you through the structure of the configuration file and provides practical examples.

## Minimal Configuration
At a minimum, you must define the dataset name and the file paths. JDEX will automatically populate all other parameters with sensible defaults. The minimum **required** inputs to JDEX are:
- `paths.schema`: The path to your custom ontology schema file
- `paths.data`: The path to you custom knowledge graph assertions file (containing RDF type assertions, meaning ObjectPropertyAssertions and ClassAssertions)

```json
{
  "dataset_name": "example_dataset",
  "paths": {
    "schema": "data/schema.owl",
    "data": "data/triples.ttl",
    "output": "output/"
  }
}
```

```{tip}
You do not need to setup all the parameters! Set only what you want, all other parameters will be automatically set to their default values!
```

## Configuration Structure Overview
The configuration is logically divided into five primary sections:
- **General Settings**: Global execution behavior.
- **Paths**: Input and output file management.
- **Reasoning**: Logic-based inference and validation settings.
- **Split**: Parameters for Machine Learning dataset partitioning.
- **Post-processing**: Export formats and mapping utilities.

### General Settings
These parameters control the environment and the Description Logic (DL) complexity handled by the engine.

```json
{
  "dataset_name": "my_dataset",
  "verbose": 1,
  "interactive_shell": true,
}
```

| Parameter                   | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| dataset_name               | A unique identifier for the project.                                       |
| verbose                    | Logging verbosity level (0 for quiet, 1 for info, 2 for debug).             |
| interactive_shell          | When true, enables interactive prompts during execution.                    |

### Paths Configuration
Defines where JDEX finds your knowledge base and where it saves processed artifacts.

```json
{
  "paths": {
    "schema": "data/schema.owl",
    "data": "data/data.ttl",
    "output": "output/"
  }
}
```

### Reasoning Configuration

The reasoning block manages JVM memory and specific inference tasks. JDEX supports multiple reasoners depending on the task.

```json
{
  "reasoning": {
    "java_max_ram": 8,
    "java_8_home": "/path/to/java8",
    "java_11_home": "/path/to/java11",
    "materialization": {
      "enabled": true,
      "reasoner": "hermit"
    },
    "realization": {
      "enabled": true,
      "reasoner": "konclude"
    },
    "satisfiability": {
      "filter_unsatisfiable": false,
      "reasoner": "hermit"
    },
    "modularization": {
      "enabled": true
    },
    "decomposition": {
      "tbox": true,
      "rbox": true
    },
    "consistency": {
      "convert_ntriples": false
    }
  }
}
```
| Parameter                              | Description                                                                                  |
|----------------------------------------|----------------------------------------------------------------------------------------------|
| java_max_ram                 | Maximum RAM (in GB) allocated to the Java reasoning process.                                 |
| java_8_home                  | Path to the Java 8 installation directory.                                                   |
| java_11_home                 | Path to the Java 11 installation directory.                                                  |
| materialization.enabled      | Enables or disables materialization (precomputing inferred knowledge).                       |
| materialization.reasoner     | Reasoner used for materialization (e.g., "hermit").                                           |
| realization.enabled          | Enables or disables realization (computing class memberships of individuals).                |
| realization.reasoner         | Reasoner used for realization (e.g., "konclude").                                             |
| satisfiability.filter_unsatisfiable | If true, filters out unsatisfiable classes.                                           |
| satisfiability.reasoner      | Reasoner used for satisfiability checking (e.g., "hermit").                                   |
| modularization.enabled       | Enables or disables ontology modularization.                                                  |
| decomposition.tbox           | Enables decomposition of the TBox (terminological axioms).                                    |
| decomposition.rbox           | Enables decomposition of the RBox (role/property axioms).                                     |
| consistency.convert_ntriples | Converts data to N-Triples format for consistency checking if enabled.                       |

### Dataset Splitting
Configure how triples are partitioned for Machine Learning tasks.

```json
{
  "split": {
    "enabled": true,
    "train_percent": 80,
    "validation_percent": 10,
    "test_percent": 10,
    "transductive": true,
    "test_leakage_filtering": {
      "enabled": true,
      "minimum_frequency": 0.97
    }
  }
}
```
**Constraints**: Percentages must sum to exactly 100.  
**Leakage Filtering**: A critical feature that prevents "data contamination" by ensuring test entities aren't overly represented in the training set based on frequency thresholds.

| Parameter                         | Description                                                                                   |
|----------------------------------|-----------------------------------------------------------------------------------------------|
| enabled                          | Enables or disables dataset splitting.                                                        |
| train_percent                    | Percentage of data assigned to the training set.                                               |
| validation_percent               | Percentage of data assigned to the validation set.                                             |
| test_percent                     | Percentage of data assigned to the test set.                                                   |
| transductive                     | If true, uses a transductive split (entities may appear across splits).                        |
| test_leakage_filtering.enabled   | Enables or disables leakage filtering for the test set.                                        |
| test_leakage_filtering.minimum_frequency | Threshold frequency for filtering entities to prevent leakage (e.g., 0.97).         |


### Post-processing
Control the final output formats for downstream consumption.

```json
{
  "post_processing": {
    "json_conversion": true,
    "id_mapping": true,
    "tsv_conversion": true
  }
}
```
| Parameter        | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| json_conversion  | Converts processed data into JSON format.                                   |
| id_mapping       | Generates mappings between original identifiers and internal IDs.           |
| tsv_conversion   | Converts processed data into TSV (tab-separated values) format.             |

```{tip}
**JSON**: Best for web apps or document databases.  
**ID Mapping**: Creates a dictionary mapping URI strings to integer IDs.  
**TSV**: Ideal for knowledge graph embedding frameworks like Pykeen or GraphVite.
```


## Full Example
A complete configuration for a standard reasoning and splitting pipeline.

```json
{
  "dataset_name": "example",
  "verbose": 1,
  "interactive_shell": true,
  "paths": {
    "schema": "data/schema.owl",
    "data": "data/triples.ttl",
    "output": "output/"
  },
  "reasoning": {
    "java_max_ram": 4,
    "materialization": {
      "enabled": true,
      "reasoner": "hermit"
    },
    "realization": {
      "enabled": true,
      "reasoner": "konclude"
    }
  },
  "split": {
    "train_percent": 80,
    "validation_percent": 10,
    "test_percent": 10
  },
  "post_processing": {
    "json_conversion": true,
    "tsv_conversion": true
  }
}
```

## Loading the Configuration in Python
You can easily interface with JDEX programmatically using the JDEXConfig class.

```python
from jdex.config import JDEXConfig
import json

# Load from file
with open("config.json", "r") as f:
    data = json.load(f)

# Instantiate the config object
config = JDEXConfig.from_dict(data)

# Verify parameters
print(config.pretty_print())
```

## Additional Notes

- **Validation**: Providing invalid values (e.g., wrong reasoner names or split percentages that don't total 100) will raise errors during initialization.
- **Modularity**: Each component (reasoning, splitting, etc.) can be toggled independently if you only need specific parts of the pipeline.