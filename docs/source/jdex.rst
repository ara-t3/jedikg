**JDeX**: Modular Extraction Tool
===================================================

JDeX Suite
----------

The JDEX suite provides a collection of modular tools for ontology processing
and dataset preparation, designed to be used both independently and as part of
a unified pipeline.

At its core, JDEX exposes several utilities directly usable in Python, including
reasoning services, ontology modularization and decomposition, as well as
conversion utilities. These components can be integrated into custom workflows
or used standalone for specific tasks, offering flexibility for advanced users.

For ease of use and end-to-end dataset generation, JDEX also provides a complete
pipeline accessible through an interactive interface and JSON-based configuration.
This allows users to run complex workflows with minimal setup while maintaining
full control over each processing step.

The following sections document each component in detail, with emphasis on their
individual usage and configuration options. A schematization of the full pipeline (with all reasoing services active) can be found below

.. figure:: jedikg.drawio.png


Reasoning Utility
--------------------

Utilities for performing reasoning over OWL ontologies using the ROBOT toolkit, Pellet, and Konclude. It automatically handles switching JAVA_HOME version to handle both Pellet JAVA 8 and ROBOT JAVA 11 requirements.

.. autoclass:: jdex.owl.reasoning.Reasoner
   :members:
   :show-inheritance:
   :undoc-members:

Modularization and Decomposition
--------------------

Modules for breaking down large ontologies or knowledge graphs into smaller, semantically meaningful components. SignatureModularizer and SchemaDecomposer enable modularization based on signatures.

.. autoclass:: jdex.owl.modularization.SignatureModularizer
   :members:
   :show-inheritance:
   :undoc-members:

.. autoclass:: jdex.owl.decomposition.SchemaDecomposer
   :members:
   :show-inheritance:
   :undoc-members:


Post Processing Utilities
--------------------

Utilities to convert and serialize ontologies and RDF data into formats usable for downstream processing.

.. autoclass:: jdex.utils.postprocessing.OWLConverter
   :members:
   :show-inheritance:
   :undoc-members:


.. autoclass:: jdex.utils.postprocessing.TSVConverter
   :members:
   :show-inheritance:
   :undoc-members:


.. autoclass:: jdex.utils.postprocessing.IDMapper
   :members:
   :show-inheritance:
   :undoc-members:


Machine Learning Loaders
--------------------

This section contains dataset loaders for PyTorch, designed to handle ontology-enriched knowledge graphs. The KnowledgeGraph class provides structured access to ABox triples, TBox taxonomies, and RBox axioms, exposing them as integer-based tensors suitable for embedding models, link prediction, and other graph-based machine learning tasks.

.. autoclass:: jdex.loaders.torch.KnowledgeGraph
   :members:
   :show-inheritance:
   :undoc-members:

Naive Inconsistencies Filtering
--------------------

.. autoclass:: jdex.utils.consistency.InconsistenciesFilterer
   :members:
   :show-inheritance:
   :undoc-members:

Naive Description Logic Profile Filtering
--------------------


.. autoclass:: jdex.owl.modularization.BaseDLProfileFilter
   :members:
   :show-inheritance:
   :undoc-members:

.. autoclass:: jdex.owl.modularization.ELProfileFilter
   :members:
   :show-inheritance:
   :undoc-members:

.. autoclass:: jdex.owl.modularization.ALCProfileFilter
   :members:
   :show-inheritance:
   :undoc-members:


Configuration Utility
--------------------

This section describes the general configuration structure used by JDEX.

It provides an overview of the available configuration classes and their
default behavior. However, it is not intended to be a complete guide for
setting up a configuration file.

For a step-by-step explanation and practical examples, please refer to the `Configuration Tutorial`

.. autoclass:: jdex.config.ReasoningConfig
   :members:
   :show-inheritance:
   :undoc-members:

.. autoclass:: jdex.config.JDEXConfig
   :members:
   :show-inheritance:
   :undoc-members:
