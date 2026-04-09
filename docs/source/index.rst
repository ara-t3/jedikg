
KG-SaF: Data and Workflow Documentation
================================================

KG-SaF-Data and KG-SaF-JDeX from "Diliso, I., Barile, R., d'Amato, C., & Fanizzi, N. (2025). KG-SaF: Building Complete and Curated Datasets for Machine Learning and Reasoning on Knowledge Graphs (Version 0.0.0.1) [Computer software]. https://doi.org/10.5281/zenodo.17817931"

**KG-SaF** provides a workflow (*KG-SaF-JDeX*) and curated datasets  (*KG-SaF-Data*) for knowledge graph refinement (KGR) research. The resource includes datasets with both **schema (ontologies)** and **ground facts**, making it ready for **machine learning** and **reasoning services**.



Key Features
------------

- 🗂️ Extracts datasets from RDF-based KGs with expressive schemas (RDFS/OWL2)  
- 📦 Provides datasets in **OWL** and **TSV** formats, easily loadable in both **PyTorch** and **Protege**  
- ⚡ Handles inconsistencies and leverages reasoning to infer implicit knowledge
- 🤖 Provides ML-ready **tensor representations** compatible with PyTorch and PyKEEN  
- 🧩 Offers **schema decomposition** into themed partitions (modularization of ontology components)

Advanced Python Reasoning Integration
-------------------------------------

- 🔌 Provides a Python abstraction layer for reasoners, tightly integrated with RDFLib, enabling seamless use of multiple engines:
   - ☕ Java-based reasoners for materialization (HermiT, Elk)
   - ⚙️ Konclude (C++) for parallelizable consistency checking and realization
   - 🧩 Pellet for justification extraction
- 🔄 Automatically detects and removes unsatisfiable classes and object properties
- 🔍 Includes tools to analyze inconsistency justifications directly in Python

Usability & Complete Customization
----------------------------------

- 🖥️ Provides an interactive CLI-based interface for easy workflow management
- ⚙️ Fully configurable via JSON, allowing you to:
   - Select which reasoners to use
   - Choose specific reasoning services (e.g., materialization, consistency check, justification)
   - Customize all parameters for dataset generation


.. toctree::
   :maxdepth: 2
   :caption: Introduction:

   quick
   config
   tutorial


.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   data
   jdex


.. toctree::
   :maxdepth: 2
   :caption: Appendix:

   reference


