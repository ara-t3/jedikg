
JediKG Suite: Official Documentation
================================================



**JediKG** provides a workflow **JDeX** (Jedi Dataset EXtraction) and curated datasets suite **JDSet** (Jedi DataSET) for knowledge graph refinement (KGR) research. The resource includes datasets with both **schema (ontologies)** and **ground facts**, making it ready for **machine learning** and **reasoning services**.

.. image:: https://img.shields.io/badge/GitHub-Repository-black?logo=github
   :target: https://github.com/ivandiliso/kg-saf
   :alt: GitHub Repository

.. image:: https://zenodo.org/badge/1110012490.svg
   :target: https://doi.org/10.5281/zenodo.17817931
   :alt: DOI

.. image:: https://img.shields.io/github/v/release/ara-t3/jedikg
   :alt: GitHub repo size

.. image:: https://img.shields.io/github/license/ara-t3/jedikg
   :alt: GitHub License

.. image:: https://img.shields.io/badge/python-3.11%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/github/stars/ara-t3/jedikg
   :alt: GitHub repo size


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
   :maxdepth: 3
   :caption: JediKG Documentation :

   data


.. toctree::
   :maxdepth: 2

   jdex


.. toctree::
   :maxdepth: 2
   :caption: Future Updates

   maintenance



.. toctree::
   :maxdepth: 2
   :caption: Appendix:

   reference
