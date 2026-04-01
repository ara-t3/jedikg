# KG-SaF: Building Complete and Curated Datasets for Machine Learning and Reasoning on Knowledge Graphs

**[NEW!]** ReadTheDocs Style Documentation Available! Click docs button down below!

[![DOI](https://zenodo.org/badge/1110012490.svg)](https://doi.org/10.5281/zenodo.17817931)
![GitHub License](https://img.shields.io/github/license/ivandiliso/sphm4kg)
![Python Version](https://img.shields.io/badge/python-3.12.8%2B-blue)
[![Docs](https://img.shields.io/badge/docs-online-success.svg)](https://ivandiliso.github.io/kg-saf/)
[![arXiv](https://img.shields.io/badge/arXiv-2602.14795-b31b1b.svg)](https://arxiv.org/abs/2602.14795)


**KG-SaF** provides a workflow (*KG-SaF-JDeX*) and curated datasets  (*KG-SaF-Data*) for knowledge graph refinement (KGR) research. The resource includes datasets with both **schema (ontologies)** and **ground facts**, making it ready for **machine learning** and **reasoning services**.

### Key Features
- 🗂️ Extracts datasets from RDF-based KGs with expressive schemas (RDFS/OWL2)  
- 📦 Provides datasets in **OWL** and **TSV** formats, easily loadable in both **PyTorch** and **Protege**  
- ⚡ Handles inconsistencies and leverages reasoning to infer implicit knowledge
- 🤖 Provides ML-ready **tensor representations** compatible with PyTorch and PyKEEN  
- 🧩 Offers **schema decomposition** into themed partitions (modularization of ontology components)
- 📄 Fully documented at [https://ivandiliso.github.io/kg-saf/](https://ivandiliso.github.io/kg-saf/)


## Dataset Documentation (*KG-SaF-Data*)

### Available Ontologies (Schema) and Datasets

The table below lists the currently available **ontologies** and their corresponding **datasets** included in this resource.  
> Note: This table will be **updated** as new datasets and ontologies become available.

| Ontology | Datasets | DL Fragment |
|----------|---------|-------------|
| 📚 [DBpedia](https://www.dbpedia.org/resources/ontology/) | `DBPEDIA25-50K-C`, `DBPEDIA25-100K-C` | $\mathcal{ALCHF}$ |
| 📚 [YAGO3](https://yago-knowledge.org/downloads/yago-3) | `YAGO3-39K-C`, `YAGO3-10-C` | $\mathcal{ALHIF+}$ |
| 📚 [YAGO4](https://yago-knowledge.org/downloads/yago-4ap) | `YAGO4-20-C` | $\mathcal{ALCHIF}$ |
| 📚 [ArCo](http://wit.istc.cnr.it/arco) | `ARCO25-20`, `ARCO25-10`, `ARCO25-5` | $\mathcal{SROIQ}$ |
| 📚 [WHOW](https://whowproject.eu/) | `WHOW25-5` | $\mathcal{SROIQ}$ |
| 📚 [ApuliaTravel](https://github.com/rbarile17/ApuliaTravelKG) | `ATRAVEL` | $\mathcal{SRIQ}$ |



### Dataset File Structure

All datasets are provided in a **standardized format** following the **Description Logic (DL) formalization**, separating the dataset into **ABox** (instance-level data), **TBox** (schema-level information), and **RBox** (roles and properties)
> 📄 Files marked with this icon are **new serializations or variations** of the same data already available in OWL format (e.g., TSV or JSON representations), intended for easier use in ML pipelines.

```
📁 abox ......................................... # Assertional Box (instance-level data)
│ ├── 📁 splits ................................. # Train/test/validation splits
│ │ ├── 🦉 train.nt ............................. # Training triples (N-Triples)
│ │ ├── 🦉 valid.nt ............................. # Validation triples (N-Triples)
│ │ ├── 🦉 test.nt .............................. # Test triples (N-Triples)
│ │ ├── 📄 train.tsv ............................ # Training triples (TSV)
│ │ ├── 📄 valid.tsv ............................ # Validation triples (TSV)
│ │ └── 📄 test.tsv ............................. # Test triples (TSV)
│ │
│ ├── 🦉 individuals.owl ........................ # Individuals definitions
│ ├── 🦉 class_assertions.owl ................... # Individuals class assertions (OWL)
│ ├── 📄 class_assertions.json .................. # Individuals class assertions (JSON)
│ │
│ ├── 🦉 obj_prop_assertions.nt ................. # Combined triples (N-Triples)
│ └── 📄 obj_prop_assertions.tsv ................ # Combined triples (TSV)

📁 rbox ......................................... # Role Box (relations and properties)
│ ├── 🦉 roles.owl .............................. # Role definitions
│ ├── 📄 roles_domain_range.json ................ # Domain and range of roles (JSON)
│ └── 📄 roles_hierarchy.json ................... # Role hierarchy (JSON)

📁 tbox ......................................... # Terminological Box (schema-level info)
│ ├── 🦉 classes.owl ............................ # Class non-taxonomical axioms
│ ├── 🦉 taxonomy.owl ........................... # Hierarchical taxonomy
│ └── 📄 taxonomy.json .......................... # Hierarchical taxonomy (JSON)

🦉 knowledge_graph.owl .......................... # Full merged TBox + RBox + ABox
🦉 ontology.owl ................................. # Core modularized schema

📁 mappings ..................................... # Mappings to IDs
│ ├── 🧾 class_to_id.json ....................... # Map ontology classes to IDs
│ ├── 🧾 individual_to_id.json .................. # Map entities/instances to IDs
│ └── 🧾 object_property_to_id.json ............. # Map object properties to IDs
```

## Dataset Unpacking 

Before using the datasets, you must run the provided **dataset unpacking notebook**. This step is required because, due to storage limitations, some secondary files were removed from the distributed datasets.  The script automates the following tasks:

1. **Unpacking all compressed datasets and ontologies** into an `unpack` folder.  
2. **Re-merging object property assertion files** for each dataset.  
3. **Merging the full knowledge graph** (TBox, RBox, and ABox) using a reasoner (Robot OBO Tool).  
4. **Converting N-Triples files to TSV format**, making them ready for use with ML libraries such as **PyKEEN**.  
5. **Converting Schema files to JSON** (e.g., class assertions, taxonomy, role hierarchies) for easier loading and manipulation in Python.

Open the notebook and **run all cells** sequentially. After execution, each dataset folder will contain:

- Fully merged **knowledge graph** (`knowledge_graph.owl`)  
- **Object property assertions** (`obj_prop_assertions.nt` and `.tsv`)  
- **Training, test, and validation splits** in TSV format (`train.tsv`, `test.tsv`, `valid.tsv`) 
- **Taxonomy, Roles, and Class Assertion** in JSON format (`taxonomy.json`, `roles_domain_range.json`, `roles_hierarchy.json`, `class_assetions.json`)

## Tutorials

In the `tutorial` folder, we provide example notebooks demonstrating how to use KG-SaF datasets and tools.

1. **Loading a PyTorch dataset using the custom `KnowledgeGraph` class**  
   - File: `tutorial/dataset_loader.ipynb`  
   - Description: Shows how to load a dataset from KG-SaF into PyTorch tensors using the `KnowledgeGraph` class, including train/test/validation splits and schema-aware representations.  

2. **Proof of concept: Using PyKEEN for machine learning on KG-SaF datasets**  
   - File: `tutorial/kge_pykeen.ipynb`  
   - Description: Demonstrates a basic pipeline for training a Knowledge Graph Embedding (KGE) model using PyKEEN on one of the KG-SaF datasets, including evaluation.  

2. **Generating a KG-SaF Dataset form a Custom KG**  
   - File: `tutorial/general.ipynb`  
   - Description: Full pipeline for transforming a user defined KG into a machine learning ready dataset. Performs all the requires preprocessing, filtering and post processing of the KG-SaF-JDeX workflow.


# Citation
```bibtex
@misc{diliso2026returnschemabuildingcomplete,
      title={Return of the Schema: Building Complete Datasets for Machine Learning and Reasoning on Knowledge Graphs}, 
      author={Ivan Diliso and Roberto Barile and Claudia d'Amato and Nicola Fanizzi},
      year={2026},
      eprint={2602.14795},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2602.14795}, 
}
```
