**JDSet**: Complete KGR Datasets
=================

JDSet provides **complete and curated knowledge graph datasets** designed for **machine learning** and **reasoning tasks**. Each dataset comes with both a **schema (TBox)** and **instance data (ABox)**, along with **role definitions (RBox)**, making them ready for Knowledge Graph Refinement (KGR) research and embedding-based pipelines.

These datasets are compatible with **Python**, **PyTorch**, **PyKEEN**, and ontology editors like **Protege**.


## Source Knowledge Graphs and Schema Expressivity

### Available Source Knowledge Graphs

JDSet includes datasets derived from **well-known knowledge graphs** and domain-specific ontologies. Each ontology is provided as part of the dataset with **modularized TBox, RBox, and ABox components**.

- **DBpedia** – [Link](https://www.dbpedia.org/resources/ontology/)  
  Large-scale multilingual knowledge graph extracted from Wikipedia. Contains general-purpose concepts like `Person`, `Place`, `Organisation`, and relationships between them.  

- **YAGO3** – [Link](https://yago-knowledge.org/downloads/yago-3)  
  Knowledge graph integrating Wikipedia, WordNet, and GeoNames. Known for high coverage and rich semantic types (`ALHIF+` DL fragment).  

- **YAGO4** – [Link](https://yago-knowledge.org/downloads/yago-4)  
  Updated version of YAGO with enhanced temporal and factual coverage, suitable for reasoning over large-scale datasets.  

- **ArCo** – [Link](http://wit.istc.cnr.it/arco)  
  Cultural heritage ontology and KG covering Italian assets. Supports advanced reasoning with `SROIQ` DL fragment.  

- **WHOW** – [Link](https://whowproject.eu/)  
  Ontology for the World Heritage and cultural objects, designed for semantic reasoning and ML experiments.  

- **ERA** – [Link](hhttps://www.era.europa.eu/domains/registers/era-knowlege-graph_en)  
  Vocabulary/Ontology governed by the European Union Agency for Railways (https://www.era.europa.eu/). It represents the concepts and relationships linked to the sectorial legal framework and the use cases under the Agency´s remit


### Knowledge Graph Schema Expressivity


| Axiom Type               | DBPedia | YAGO3 | YAGO4 | WHOW | ARCO | ERA |
| ------------------------ | ------- | ----- | -------- | ------ | ------ | --- |
| ClassAssertion           | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| SubClassOf               | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| EquivalentClasses        | -       | -     | -        | -      | ✅      | -   |
| DisjointClasses          | ✅       | -     | ✅        | ✅      | ✅      | ✅   |
| UnionOf                  | -       | -     | ✅        | ✅      | ✅      | ✅   |
| IntersectionOf           | -       | -     | -        | -      | -      | -   |
| ComplementOf             | -       | -     | -        | -      | ✅      | -   |
| Existential Restrictions | -       | -     | -        | ✅      | ✅      | -   |
| Universal Restrictions   | -       | -     | -        | ✅      | ✅      | ✅   |
| Cardinality Restrictions | -       | -     | -        | ✅      | ✅      | ✅   |
| ObjPropDomain            | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| ObjPropRange             | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| SubObjProp               | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| InverseObjProp           | -       | -     | ✅        | ✅      | ✅      | ✅   |
| EquivalentObjProp        | ✅       | -     | -        | ✅      | ✅      | ✅   |
| ObjPropCharacteristic    | ✅       | ✅     | ✅        | ✅      | ✅      | ✅   |
| ObjPropChain             | -       | -     | ✅        | ✅      | ✅      | -   |


## JDSet Data File Structure

JDSet datasets follow a **Description Logic (DL) formalization**, organizing the knowledge graph into three main components:

- **ABox (Assertional Box):** Instance-level data (entities, class assertions, object property assertions)  
- **TBox (Terminological Box):** Schema-level knowledge, including class hierarchies and axioms  
- **RBox (Role Box):** Relationships and properties, including domain, range, and hierarchy  


```{note} 
📄 Files marked with this icon are **new serializations or variations** of the same data already available in OWL format (e.g., TSV or JSON representations), intended for easier use in ML pipelines.
```

Each dataset folder contains the following structure:

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




## Datasets Statistics

The tables below list the available **ontologies** and their corresponding **datasets** included in this resource.

```{note}
For each metric, values in parentheses correspond to the dataset obtained after applying reasoning services (i.e., materialization and realization).
```

### Basic Informations: Entities, Roles and Classes

| Dataset          | DL Fragment | Entities | Roles (Schema) | Classes | Roles (Facts) |
| ---------------- | ----------- | -------- | ----- | ------- | --- |
| `DBPEDIA_50K_C`  | ALCHF       | 22,263   | 278   | 372     | 275 |
| `DBPEDIA_100K_C` | ALCHF       | 96,366   | 409   | 472     | 406 |
| `YAGO3_39K_C`    | ALHIF+      | 37,711   | 35    | 46,892  | 34 |
| `YAGO3_10_C`     | ALHIF+      | 123,038  | 35    | 94,726  | 34 |
| `YAGO4_20_C`     | ALCHIF      | 91,904   | 69    | 1,462   | 68 |
| `ARCO_20`        | SROIQ       | 15,826   | 452   | 300     | 53 |
| `ARCO_10`        | SROIQ       | 45,524   | 591   | 392     | 111 |
| `ARCO_5`         | SROIQ       | 198,792  | 681   | 422     | 195 |
| `WHOW_5`         | SROIQ       | 137,741  | 102   | 90      | 25 |
| `ERA_90`         | ALCRIQ      | 50,311   | 82    | 41      | 42 |
| `ERA_95`         | ALCRIQ      | 18,046   | 80    | 41      | 40 |

### Assertions Quantity Informations

| Dataset          | Assertions (Raw / Materialized) | Object Property Assertions | Class Assertions (Raw / Materialized) |
| ---------------- | ------------------------------- | -------------------------- | ------------------------------------- |
| `DBPEDIA_50K_C`  | 40,929 / 199,864                | 28,516                     | 12,413 / 171,348                      |
| `DBPEDIA_100K_C` | 659,575 / 1,535,171             | 576,927                    | 82,648 / 958,244                      |
| `YAGO3_39K_C`    | 811,977 / 1,338,258             | 369,987                    | 441,990 / 968,271                     |
| `YAGO3_10_C`     | 2,390,332 / 4,204,994           | 1,080,369                  | 1,309,963 / 3,124,625                 |
| `YAGO4_20_C`     | 770,128 / 896,875               | 653,988                    | 116,140 / 242,887                     |
| `ARCO_20`        | 137,462 / 215,465               | 95,840                     | 41,622 / 119,625                      |
| `ARCO_10`        | 321,792 / 541,175               | 202,492                    | 119,300 / 344,683                     |
| `ARCO_5`         | 1,125,075 / 2,140,161           | 655,048                    | 471,027 / 1,485,113                   |
| `WHOW_5`         | 729,682 / 1,250,448             | 584,791                    | 144,891 / 665,657                     |
| `ERA_90`         | 1,937,084 / 2,134,171           | 1,886,773                  | 50,311 / 247,398                      |
| `ERA_95`         | 483,497 / 551,718               | 465,451                    | 18,046 / 86,267                       |

### Relation Cardinality Pattens Distribution

| Dataset          | 1 to 1   | 1 to N  | N to 1   | N to N   |
| ---------------- | ----- | ----- | ----- | ----- |
| `ARCO_10`        | 0.072 | 0.072 | **0.703** | 0.153 |
| `ARCO_20`        | 0.075 | 0.113 | **0.698** | 0.113 |
| `ARCO_5`         | 0.144 | 0.072 | **0.631** | 0.154 |
| `DBPEDIA_100K_C` | 0.296 | 0.111 | **0.362** | 0.232 |
| `DBPEDIA_50K_C`  | **0.545** | 0.029 | 0.418 | 0.007 |
| `ERA_90`         | 0.000 | 0.024 | **0.714** | 0.262 |
| `ERA_95`         | 0.000 | 0.025 | **0.775** | 0.200 |
| `WHOW_5`         | 0.040 | 0.000 | **0.920** | 0.040 |
| `YAGO3_10_C`     | 0.059 | 0.147 | 0.294 | **0.500** |
| `YAGO3_39K_C`    | 0.206 | 0.029 | **0.412** | 0.353 |
| `YAGO4_20_C`     | 0.221 | 0.147 | **0.485** | 0.147 |

### Reasoning Performance

```{note}
ROFF and RON refer to reasoning configurations with reasoning services disabled and enabled, respectively.
```

| Dataset Name     | Runtime (ROFF) | Runtime (RON) | Realization Time | Materialization Time | Reasoner |
| ---------------- | -------------- | ------------- | ---------------- | -------------------- | -------- |
| `ARCO_20`        | 66.23 s        | 369.12 s      | 4.78 s           | 280.13 s             | Konclude |
| `ARCO_10`        | 77.29 s        | 415.30 s      | 10.15 s          | 280.13 s             | Konclude |
| `ARCO_5`         | 231.09 s       | 435.56 s      | 38.45 s          | 280.13 s             | Konclude |
| `WHOW_5`         | 153.66 s       | 256.47 s      | 19.33 s          | 36.22 s              | Konclude |
| `YAGO4_20_C`     | 200.11 s       | 282.41 s      | 16.00 s          | 18.18 s              | Konclude |
| `YAGO3_10_C`     | 579.32 s       | 2321.29 s     | 202.12 s         | 149.48 s             | ELK      |
| `YAGO3_39K_C`    | 265.51 s       | 1444.88 s     | 169.84 s         | 149.48 s             | ELK      |
| `DBPEDIA_50K_C`  | 30.60 s        | 43.49 s       | 4.40 s           | 14.75 s              | Konclude |
| `DBPEDIA_100K_C` | 200.43 s       | 114.01 s      | 9.47 s           | 14.75 s              | Konclude |
| `ERA_95`         | 90.99 s        | 98.12 s       | 6.40 s           | 5.62 s               | Konclude |
| `ERA_90`         | 90.99 s        | 236.68 s      | 18.90 s          | 5.62 s               | Konclude |


## Knowledge Graph Embedding Benchmarks

This section will be updated as new ontologies or dataset are supported by our suite!

```{warning}
The following results are proof-of-concept experiments. They are intended to showcase preliminary performance trends across models rather than provide a fully optimized or exhaustive benchmark.
```

**Datasets from `YAGO3`**

| Dataset   | Model   | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
| --------- | ------- | ------- | ----- | ------ | ------ | ------- |
| YAGO3-39K | TransE  | 1908.55 | 0.127 | 0.048  | 0.201  | 0.289   |
| YAGO3-39K | RotatE  | 483.47  | 0.225 | 0.140  | 0.298  | 0.391   |
| YAGO3-39K | ComplEx | 6885.38 | 0.053 | 0.022  | 0.073  | 0.112   |
| YAGO3-39K | CompGCN | 1810.08 | 0.138 | 0.078  | 0.183  | 0.252   |

**Datasets from `YAGO4`**

| Dataset  | Model   | MR       | MRR   | Hits@1 | Hits@5 | Hits@10 |
| -------- | ------- | -------- | ----- | ------ | ------ | ------- |
| YAGO4-20 | TransE  | 2454.366 | 0.112 | 0.026  | 0.199  | 0.260   |
| YAGO4-20 | RotatE  | 1675.701 | 0.365 | 0.297  | 0.438  | 0.494   |
| YAGO4-20 | ComplEx | 5422.310 | 0.070 | 0.045  | 0.090  | 0.115   |
| YAGO4-20 | CompGCN | 1711.996 | 0.194 | 0.124  | 0.257  | 0.332   |

**Datasets from `WHOW`**

| Dataset | Model   | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
| ------- | ------- | ------- | ----- | ------ | ------ | ------- |
| WHOW-5  | TransE  | 4482.41 | 0.123 | 0.003  | 0.251  | 0.349   |
| WHOW-5  | RotatE  | 1314.55 | 0.529 | 0.417  | 0.673  | 0.766   |
| WHOW-5  | ComplEx | 9235.94 | 0.055 | 0.040  | 0.070  | 0.084   |
| WHOW-5  | CompGCN | 733.29  | 0.422 | 0.304  | 0.566  | 0.625   |

**Datasets from `ARCO`**

| Dataset | Model   | MR       | MRR   | Hits@1 | Hits@5 | Hits@10 |
| ------- | ------- | -------- | ----- | ------ | ------ | ------- |
| ARCO-10 | TransE  | 914.077  | 0.200 | 0.010  | 0.414  | 0.514   |
| ARCO-10 | RotatE  | 428.235  | 0.759 | 0.680  | 0.845  | 0.867   |
| ARCO-10 | ComplEx | 1741.747 | 0.192 | 0.131  | 0.258  | 0.308   |
| ARCO-10 | CompGCN | 359.778  | 0.572 | 0.459  | 0.702  | 0.751   |

**Datasets from `DBPedia`**

| Dataset      | Model   | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
| ------------ | ------- | ------- | ----- | ------ | ------ | ------- |
| DBPEDIA-100K | TransE  | 3005.94 | 0.114 | 0.012  | 0.219  | 0.294   |
| DBPEDIA-100K | RotatE  | 2693.98 | 0.371 | 0.282  | 0.468  | 0.541   |
| DBPEDIA-100K | ComplEx | 7243.17 | 0.116 | 0.056  | 0.176  | 0.223   |
| DBPEDIA-100K | CompGCN | 1659.33 | 0.198 | 0.099  | 0.299  | 0.396   |
