# Tutorials and Guides

## Loading and Analyzing a KG-SaF Datasets in PyTorch 

This tutorial demonstrates how to load a Knowledge Graph dataset using kgsaf_jdex and inspect its components, classes, and object property hierarchies. You can find a full executable Notebook in `tutorial/dataset_loader.ipynb`. For this example the `APULIATRAVEL` dataset will be used.

**Setup and Imports**

Before loading the dataset, make sure your Python environment can access the library and required modules:

```python
import sys
sys.path.append(str(Path.cwd().parent))  # Adds the parent folder to the path
import json
import random
from pathlib import Path
import kgsaf_jdex.utils.conventions.paths as pc
from kgsaf_jdex.loaders.pytorch.dataset import KnowledgeGraph
```

```{tip}
Adding the parent directory to `sys.path` allows Python to locate your `kgsaf_jdex` package if it is not installed system-wide.
```

### Loading the Dataset

Use the `KnowledgeGraph` class to load a dataset from the folder created by the unpacking utility:

```python
kg = KnowledgeGraph(
    path="<DATASET_PATH>"
)
```

### Inspect Dataset Components

You can quickly inspect the shapes of the main dataset components:

```python
print(f"{'Dataset Component':<35} | {'Shape'}")
print("-" * 50)
print(f"{'Training triples':<35} | {kg.train.shape}")
print(f"{'Test triples':<35} | {kg.test.shape}")
print(f"{'Validation triples':<35} | {kg.valid.shape}")
print(f"{'Class assertions':<35} | {kg.class_assertions.shape}")
print(f"{'Taxonomy (TBox)':<35} | {kg.taxonomy.shape}")
print(f"{'Object property hierarchy':<35} | {kg.obj_props_hierarchy.shape}")
print(f"{'Object property domains':<35} | {kg.obj_props_domain.shape}")
print(f"{'Object property ranges':<35} | {kg.obj_props_range.shape}")
```

```text
Dataset Component                   | Shape
--------------------------------------------------
Training triples                    | torch.Size([65401, 3])
Test triples                        | torch.Size([7695, 3])
Validation triples                  | torch.Size([3847, 3])
Class assertions                    | torch.Size([35915, 2])
Taxonomy (TBox)                     | torch.Size([54, 2])
Object property hierarchy           | torch.Size([11, 2])
Object property domains             | torch.Size([71, 2])
Object property ranges              | torch.Size([69, 2])
```

### Exploring Individuals Classes and Object Properties

You can select random elements for testing:

```python
individual_uri_test = random.choice(list(kg._individual_to_id.keys()))
class_uri_test = random.choice(list(kg._class_to_id.keys()))
op_uri_test = random.choice(list(kg._obj_prop_to_id.keys()))

print(f"Testing on individual: {individual_uri_test}")
print(f"Testing on class: {class_uri_test}")
print(f"Testing on object property: {op_uri_test}")

```

```text
Testing on individual: https://w3id.org/italia/onto/CLV/StreetToponym/31148_Castello_street_toponym
Testing on class: https://apuliatravel.org/td/HistoricPalace
Testing on object property: https://w3id.org/italia/onto/CLV/hasDirectHigherRank
```

### Inspecting Class Assertions

Retrieve all classes associated with an individual:

```python
cls = kg.individual_classes(kg.individual_to_id(individual_uri_test)).tolist()
print(f"Class assertions for [{kg.individual_to_id(individual_uri_test)}] {individual_uri_test}:")
for c in cls:
    print(f"\t[{c}] {kg.id_to_class(c)}")
```
```text
Testing the Class Assertions of [7157] https://w3id.org/italia/onto/CLV/StreetToponym/31148_Castello_street_toponym
	 Tensor [58]
	 [58] https://w3id.org/italia/onto/CLV/StreetToponym
```

### Exploring Class Hierarchies

Check superclasses and subclasses of a given class:

```python
sup_cls = kg.sup_classes(kg.class_to_id(class_uri_test)).tolist()
sub_cls = kg.sub_classes(kg.class_to_id(class_uri_test)).tolist()

print("Superclasses:")
for c in sup_cls:
    print(f"\t[{c}] {kg.id_to_class(c)}")

print("Subclasses:")
for c in sub_cls:
    print(f"\t[{c}] {kg.id_to_class(c)}")
```

```text
Testing the Hierarchy of [84] https://w3id.org/italia/onto/TI/Year. Leaf class? True
	 Superclasses
		 Tensor: [81]
		 [81] https://w3id.org/italia/onto/TI/TemporalEntity
	 Subclasses
		 Tensor: []
```

```{note}
`is_leaf(class_id)` can be used to check if the class is a leaf in the hierarchy.
```

### Inspecting Object Properties Hierarchies

Check super and sub properties, as well as domains and ranges:

```python
sup_op = kg.sup_obj_prop(kg.obj_prop_to_id(op_uri_test)).tolist()
sub_op = kg.sub_obj_prop(kg.obj_prop_to_id(op_uri_test)).tolist()

print("Super Object Properties:")
for c in sup_op:
    print(f"\t[{c}] {kg.id_to_obj_prop(c)}")

print("Sub Object Properties:")
for c in sub_op:
    print(f"\t[{c}] {kg.id_to_obj_prop(c)}")

domain = kg.obj_prop_domain(kg.obj_prop_to_id(op_uri_test)).tolist()
range = kg.obj_prop_range(kg.obj_prop_to_id(op_uri_test)).tolist()

print("Domain:")
for c in domain:
    print(f"\t[{c}] {kg.id_to_class(c)}")

print("Range:")
for c in range:
    print(f"\t[{c}] {kg.id_to_class(c)}")

```

```text
Testing the Role Hierarhcy of [41] https://w3id.org/italia/onto/SM/hasEmailType
	 Super Obj Prop
		 Tensor: []
	 Sub Obj Prop
		 Tensor: []

Testing the Role Hierarhcy of [41] https://w3id.org/italia/onto/SM/hasEmailType
	 Domain
		 Tensor: [66]
		 [66] https://w3id.org/italia/onto/SM/Email
	 Range
		 Tensor: [67]
		 [67] https://w3id.org/italia/onto/SM/EmailType
```

## Running TransE on KG-SaF Datasets

This tutorial demonstrates how to train and evaluate **TransE** KGR model
on a dataset prepared with the `kgsaf_jdex` loaders.  You can find a full executable Notebook in `tutorial/kge_pykeen.ipynb`. The example will use the `APULIATRAVEL` dataset.

```{note}
Make sure the dataset is unpacked and the paths in `pc` (paths conventions) point to the correct files.
```

**Imports**

This code imports all necessary packages, including PyKEEN for knowledge graph embeddings and
your kgsaf_jdex dataset utilities.

```python
import sys
from pathlib import Path
import json

from pykeen.triples import TriplesFactory
from pykeen.evaluation import RankBasedEvaluator
from pykeen.pipeline import pipeline

import kgsaf_jdex.utils.conventions.paths as pc

# Add parent folder to Python path if needed
sys.path.append(str(Path.cwd().parent))
```

### Loading and Mapping Triples

Here we load entity and relation mappings from JSON files, and then build TriplesFactory objects
for training, validation, and testing. PyKEEN uses these to manage KG data efficiently.

```python
dataset_path = Path("/home/navis/dev/kg-saf/kgsaf_data/datasets/base/unpack/APULIATRAVEL-BASE")

# Load entity and relation mappings
with open(dataset_path / pc.INDIVIDUAL_MAPPINGS, "r") as f:
    entity_mapping = json.load(f)

with open(dataset_path / pc.OBJ_PROP_MAPPINGS, "r") as f:
    relation_mapping = json.load(f)

# Create PyKEEN TriplesFactory objects
train_tf = TriplesFactory.from_path(
    dataset_path / pc.TRAIN,
    entity_to_id=entity_mapping,
    relation_to_id=relation_mapping,
)

valid_tf = TriplesFactory.from_path(
    dataset_path / pc.VALID,
    entity_to_id=entity_mapping,
    relation_to_id=relation_mapping,
)

test_tf = TriplesFactory.from_path(
    dataset_path / pc.TEST,
    entity_to_id=entity_mapping,
    relation_to_id=relation_mapping,
)
```

### Train TransE Model

This code trains a TransE model using the dataset we just loaded. The pipeline function handles
everything: model initialization, training, validation, and testing.

```python
result = pipeline(
    model="TransE",
    training=train_tf,
    validation=valid_tf,
    testing=test_tf,
    model_kwargs=dict(embedding_dim=100),
    training_kwargs=dict(num_epochs=25, batch_size=128),
    device="cpu"
)
```

```
INFO:pykeen.pipeline.api:Using device: cpu
INFO:pykeen.nn.representation:Inferred unique=False for Embedding()
INFO:pykeen.nn.representation:Inferred unique=False for Embedding()
Training epochs on cpu: 100% 5/5 [00:30<00:00,  6.71s/epoch, loss=0.141, prev_loss=0.182]
Evaluating on cpu: 100% 7.70k/7.70k [01:09<00:00, 109triple/s]
INFO:pykeen.evaluation.evaluator:Evaluation took 69.78s seconds
```

```{note}
You can replace `"TransE"` with any other PyKEEN model, e.g., `"DistMult"`, `"ComplEx"`, etc.
`embedding_dim`, `num_epochs`, and `batch_size` can be adjusted depending on your dataset size.
```

### Evaluation

This code evaluates the trained model using filtered ranking metrics, such as MRR and Hits@K.
Filtered evaluation ignores triples already seen in training/validation to avoid penalizing correct predictions.

```python
evaluator = RankBasedEvaluator(filtered=True)

results = evaluator.evaluate(
    model=result.model,
    mapped_triples=test_tf.mapped_triples,
    additional_filter_triples=[
        train_tf.mapped_triples,
        valid_tf.mapped_triples,
    ],
)
results.to_dict()
```

```text
Evaluating on cpu: 100% 7.70k/7.70k [01:19<00:00, 86.9triple/s]
INFO:pykeen.evaluation.evaluator:Evaluation took 79.32s seconds
```



## Using KG-SaF-JDeX on Custom Knowledge Graphs

```{warning}
Please follow the **Quick Start Guide** before going forward.
```

```{note}
This guide is also available as a Notebook in `tutorial/general.ipynb`, a Python shell executable script in `tutorial/general.py` and shell script `tutorial/general.sh`
```

This guide show how to use the provided **KG-SaF-JDeX Workflow** Functionalities to generate a new Schema and Data Dataset from your custom Knowledge Graph.  This guide provides an example dataset in the INPUT folder to test the functionalities. All the produces files will be created in the OUTPUT folder.  

This notebook expectes the following inputs:

- Any Knowledge Graph with both Schema and Data in a unique file (any format supported by the ROBOT Utility, the file will be converted to an intermediate OWL File)
- The KG need to contain ABox assertions (object property assertions) in order to safely run the machine learning splitting and necessary checks
- This module is specifically designed for generating dataset from Knowledge graphs that contain rich schema and large scale ABox (object property assertions)

And applies the following procedures following the KG-SaF-JDeX workflow:

- Conversion to OWL Format
- Consistency Check
- Removal of Unsatisfiable Classes
- Materialization and Realization
- Filtering of ABox Individuals and Object Properties
- Object Propety Assertion splitting using Coverage Criterion in Training, Test and Validatin Split
- Inversion Leakage check and filtering
- Class Assertions subset computation
- Schema Modularization based on ABox Signature
- Schema Decomposition in TBox and RBox (with subsequent division in Schema and Taxonomy)
- Full cleaned Ontology and Knowledge Graph Reconstruction
- Conversion and serialization of object property assertion to TSV format
- Conversion and serialization of schema axioms to JSON format


#### Full pipeline script 

**Usage example:**

```bash
python3 general.py \
    --kg_file /path/to/input_kg.owl \
    --output_path /path/to/output/folder \
    --dataset_name MY_DATASET \
    --robot_jar /path/to/robot.jar \
    [--reasoner]
```

| Argument         | Description                                                                         |
| ---------------- | ----------------------------------------------------------------------------------- |
| `--kg_file`      | Path to your input KG (OWL/RDF file).                                               |
| `--output_path`  | Folder where the processed dataset and splits will be saved.                        |
| `--dataset_name` | Base name for the dataset. Reasoned datasets will append `_reasoned` otherwise `_base`.               |
| `--robot_jar`    | Path to the ROBOT JAR file (used for merging and reasoning).                        |
| `--reasoner`     | Optional flag. If set, reasoning and unsatisfiable class removal will be performed. |
