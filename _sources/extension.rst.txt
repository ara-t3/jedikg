PyKEEN Extension
=================

Constants
--------------------------

This module defines shared constant values used throughout the PyKEEN negative sampler extension.
These constants ensure consistency and avoid hardcoding fixed values across the implementation.
Typical contents include default parameter values, files naming conventions.

.. automodule:: extension.constants
   :members:
   :show-inheritance:
   :undoc-members:

Dataset
------------------------

Custom dataset loader designed to extend PyKEEN's dataset handling.
Enables support for additional metadata, filtering logic, and preprocessing tailored
to advanced negative sampling strategies.

.. automodule:: extension.dataset
   :members:
   :show-inheritance:
   :undoc-members:

Filtering
--------------------------

Implements extended filtering mechanisms for training and evaluation.
Includes logic for excluding invalid or null-indexed negatives, such as with the NullPythonSetFilterer.

.. automodule:: extension.filtering
   :members:
   :show-inheritance:
   :undoc-members:

Sampling
-------------------------

Defines custom negative sampling strategies with support for static and dynamic approaches.
Built to integrate seamlessly with PyKEEN’s pipeline while enabling schema-aware, type-based,
and model-driven sampling logic.

.. automodule:: extension.sampling
   :members:
   :show-inheritance:
   :undoc-members:
