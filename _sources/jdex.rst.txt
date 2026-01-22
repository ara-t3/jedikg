**KG-SaF-JDeX**: Modular Dataset Generation Workflow
=================


Machine Learning Loaders
--------------------

This section contains dataset loaders for PyTorch, designed to handle ontology-enriched knowledge graphs. The KnowledgeGraph class provides structured access to ABox triples, TBox taxonomies, and RBox axioms, exposing them as integer-based tensors suitable for embedding models, link prediction, and other graph-based machine learning tasks.

.. autoclass:: kgsaf_jdex.loaders.pytorch.dataset.KnowledgeGraph
   :members:
   :show-inheritance:
   :undoc-members:

Reasoning Utilities
--------------------

Utilities for performing reasoning over OWL ontologies using the ROBOT toolkit. ReasonerUtility supports tasks such as OWL conversion, reasoning with HermiT, filtering unsatisfiable classes, and serializing RDFLib graphs to OWL, making it easy to automate ontology preprocessing and inference pipelines.


.. autoclass:: kgsaf_jdex.utils.reason.ReasonerUtility
   :members:
   :show-inheritance:
   :undoc-members:


Modularization and Decomposition
--------------------

Modules for breaking down large ontologies or knowledge graphs into smaller, semantically meaningful components. SignatureModularizer and SchemaDecomposer enable modularization based on signatures.

.. autoclass:: kgsaf_jdex.utils.modularization.SignatureModularizer
   :members:
   :show-inheritance:
   :undoc-members:

.. autoclass:: kgsaf_jdex.utils.modularization.SchemaDecomposer
   :members:
   :show-inheritance:
   :undoc-members:


Conversion Utilities
--------------------

Utilities to convert and serialize ontologies and RDF data into formats usable for downstream processing.

.. autoclass:: kgsaf_jdex.utils.conversion.OWLConverter
   :members:
   :show-inheritance:
   :undoc-members:


.. autoclass:: kgsaf_jdex.utils.conversion.TSVConverter
   :members:
   :show-inheritance:
   :undoc-members:


.. autoclass:: kgsaf_jdex.utils.conversion.IDMapper
   :members:
   :show-inheritance:
   :undoc-members:




