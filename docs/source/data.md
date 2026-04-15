KGSaF **Data**: Complete KGR Datasets
=================

KG-SaF-Data provides **complete and curated knowledge graph datasets** designed for **machine learning** and **reasoning tasks**. Each dataset comes with both a **schema (TBox)** and **instance data (ABox)**, along with **role definitions (RBox)**, making them ready for Knowledge Graph Refinement (KGR) research and embedding-based pipelines.

These datasets are compatible with **Python**, **PyTorch**, **PyKEEN**, and ontology editors like **Protege**.


## Dataset Structure 

KG-SaF datasets follow a **Description Logic (DL) formalization**, organizing the knowledge graph into three main components:

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


## Available Ontologies


KG-SaF includes datasets derived from **well-known knowledge graphs** and domain-specific ontologies. Each ontology is provided as part of the dataset with **modularized TBox, RBox, and ABox components**.

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

- **ApuliaTravel** – [Link](https://github.com/rbarile17/ApuliaTravelKG)  
  Domain-specific KG for tourism in Apulia, Italy. Models attractions, accommodations, and travel routes.


## Available Datasets

The table below lists the currently available **ontologies** and their corresponding **datasets** included in this resource.  

```{note}
This table will be **updated** as new datasets and ontologies become available.
```

| Ontology      | Dataset              | DL Fragment |
|---------------|--------------------|-------------|
| DBpedia       | DBPEDIA25-50K-C    | ALCHF       |
| DBpedia       | DBPEDIA25-100K-C   | ALCHF       |
| YAGO3         | YAGO3-39K-C        | ALHIF+      |
| YAGO3         | YAGO3-10-C         | ALHIF+      |
| YAGO4         | YAGO4-20-C         | ALCHIF      |
| ArCo          | ARCO25-20          | SROIQ       |
| ArCo          | ARCO25-10          | SROIQ       |
| ArCo          | ARCO25-5           | SROIQ       |
| WHOW          | WHOW25-5           | SROIQ       |
| ApuliaTravel  | ATRAVEL            | SRIQ        |


## Dataset Statistics

### Table: Available datasets schema axiom coverage comparison

**Legend:**

- ✅ = axiom available in the dataset  
- ❌ = axiom not available  
- ⚠️ = axiom available in the KG but not in the dataset


| Axiom Type                    | DB100K-C | YAGO3-10-C | YAGO4-20-C | APULIA | WHOW-5 | ARCO-5 |
|-------------------------------|----------|------------|------------|--------|--------|--------|
| ClassAssertion                | ✅       | ✅         | ✅         | ✅     | ✅     | ✅     |
| SubClassOf                    | ✅       | ✅         | ✅         | ✅     | ✅     | ✅     |
| EquivalentClasses             | ❌       | ❌         | ❌         | ✅     | ❌     | ✅     |
| DisjointClasses               | ✅       | ❌         | ✅         | ✅     | ✅     | ✅     |
| UnionOf                       | ❌       | ❌         | ✅         | ✅     | ✅     | ✅     |
| IntersectionOf                | ❌       | ❌         | ❌         | ❌     | ❌     | ❌     |
| ComplementOf                  | ❌       | ❌         | ❌         | ✅     | ❌     | ✅     |
| Existential Restrictions      | ❌       | ❌         | ❌         | ✅     | ✅     | ✅     |
| Universal Restrictions        | ❌       | ❌         | ❌         | ✅     | ✅     | ✅     |
| Cardinality Restrictions      | ❌       | ❌         | ❌         | ✅     | ✅     | ✅     |
| ObjPropDomain                 | ✅       | ✅         | ✅         | ✅     | ✅     | ✅     |
| ObjPropRange                  | ✅       | ✅         | ✅         | ✅     | ✅     | ✅     |
| SubObjProp                     | ✅       | ✅         | ✅         | ✅     | ✅     | ✅     |
| InverseObjProp                | ❌       | ❌         | ✅         | ✅     | ✅     | ✅     |
| EquivalentObjProp             | ⚠️       | ❌         | ❌         | ✅     | ✅     | ✅     |
| ObjPropCharacteristic         | ⚠️       | ✅         | ✅         | ✅     | ✅     | ✅     |
| ObjPropChain                  | ❌       | ❌         | ✅         | ✅     | ✅     | ✅     |


### Table: Available datasets statistics

Dataset statistics including **ABox** (instance-level) and **Schema/TBox** (class & property-level) information. For object property structural columns, the **highest values** in each column are highlighted in bold (manually indicated with **…**).  

| Dataset      | Triples   | Inds     | Props | Classes | 1to1  | 1toN  | Nto1  | NtoN  | Avg Triples | Class Assert. | TBox Classes | Disjoints | Subclass | ∃R.C | ∀R.C | Props | Domain | Range | Both | Functional |
|--------------|----------:|---------:|------:|--------:|:-----:|:-----:|:-----:|:-----:|------------:|---------------:|-------------:|----------:|---------:|:----:|:----:|------:|:------:|:-----:|:----:|:-----------:|
| DB-50K-C     | 28,525    | 22,268   | 275   | 169     | 0.21  | 0.08  | 0.33  | **0.38** | 103.73      | 12,419        | 232          | 14        | 226      | -    | -    | 280   | 194    | 217   | 152  | -           |
| DB-100K-C    | 577,249   | 96,375   | 406   | 229     | 0.09  | 0.06  | 0.15  | **0.71** | 1,421.80    | 82,750        | 297          | 14        | 290      | -    | -    | 411   | 295    | 317   | 233  | -           |
| Y3-10-C      | 1,080,398 | 123,038  | 34    | 92,539  | 0.00  | 0.00  | 0.12  | **0.88** | 31,776.41   | 1,309,964     | 94,726       | -         | 94,809   | -    | -    | 35    | 34     | 29    | 28   | 12          |
| Y3-39K-C     | 370,169   | 37,711   | 34    | 45,456  | 0.03  | 0.03  | 0.15  | **0.79** | 10,887.32   | -             | 46,892       | -         | 46,960   | -    | -    | 35    | 34     | 29    | 28   | 10          |
| Y4-20-C      | 653,988   | 91,904   | 68    | 1,433   | 0.07  | 0.07  | 0.13  | **0.72** | 9,617.47    | 116,141       | 1,462        | 9         | 1,665    | -    | -    | 69    | 68     | 56    | 56   | 6           |
| ATRAVEL      | 76,943    | 29,767   | 25    | 53      | **0.36** | 0.16  | **0.36** | 0.12 | 3,077.72    | 35,910        | 100          | 12        | 184      | 17   | 52   | 71    | 57     | 61    | 47   | 16          |
| WHOW-5       | 584,791   | 137,740  | 25    | 31      | 0.00  | 0.00  | **0.76** | 0.24 | 23,391.64   | 144,892       | 91           | 16        | 202      | 43   | 34   | 102   | 99     | 99    | 99   | -           |
| ARCO-20      | 95,840    | 15,690   | 53    | 78      | 0.04  | 0.09  | 0.40  | **0.47** | 1,808.30    | 41,626        | 315          | 14        | 873      | 181  | 366  | 454   | 348    | 352   | 271  | 62          |
| ARCO-10      | 202,492   | 45,400   | 111   | 117     | 0.06  | 0.06  | **0.44** | **0.44** | 1,824.25  | 119,304       | 378          | 24        | 1,033    | 211  | 431  | 593   | 462    | 465   | 369  | 71          |
| ARCO-5       | 655,089   | 198,674  | 196   | 192     | 0.10  | 0.10  | **0.40** | **0.40** | 3,342.29 | 471,031       | 438          | 26        | 1,153    | 228  | 474  | 683   | 546    | 551   | 450  | 84          |

## Knowledge Graph Embedding Benchmarks

This section will be updated as new ontologies or dataset are supported by our suite!

```{warning}
The following results are proof-of-concept experiments. They are intended to showcase preliminary performance trends across models rather than provide a fully optimized or exhaustive benchmark.
```




### Datasets from `YAGO3`

| Dataset        | Model    | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
|----------------|----------|----------|--------|--------|--------|---------|
| YAGO3-39K      | TransE   | 1908.55 | 0.127 | 0.048 | 0.201 | 0.289 |
| YAGO3-39K      | RotatE   | 483.47  | 0.225 | 0.140 | 0.298 | 0.391 |
| YAGO3-39K      | ComplEx  | 6885.38 | 0.053 | 0.022 | 0.073 | 0.112 |
| YAGO3-39K      | CompGCN  | 1810.08 | 0.138 | 0.078 | 0.183 | 0.252 |

### Datasets from `YAGO4`

| Dataset   | Model    | MR       | MRR   | Hits@1 | Hits@5 | Hits@10 |
|-----------|----------|----------|--------|--------|--------|---------|
| YAGO4-20  | TransE   | 2454.366 | 0.112 | 0.026 | 0.199 | 0.260  |
| YAGO4-20  | RotatE   | 1675.701 | 0.365 | 0.297 | 0.438 | 0.494  |
| YAGO4-20  | ComplEx  | 5422.310 | 0.070 | 0.045 | 0.090 | 0.115  |
| YAGO4-20  | CompGCN  | 1711.996 | 0.194 | 0.124 | 0.257 | 0.332      |

### Datasets from `WHOW`

| Dataset        | Model    | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
|----------------|----------|----------|--------|--------|--------|---------|
| WHOW-5         | TransE   | 4482.41 | 0.123 | 0.003 | 0.251 | 0.349 |
| WHOW-5         | RotatE   | 1314.55 | 0.529 | 0.417 | 0.673 | 0.766 |
| WHOW-5         | ComplEx  | 9235.94 | 0.055 | 0.040 | 0.070 | 0.084 |
| WHOW-5         | CompGCN  | 733.29  | 0.422 | 0.304 | 0.566 | 0.625 |

### Datasets from `ARCO`

| Dataset  | Model    | MR       | MRR   | Hits@1 | Hits@5 | Hits@10 |
|----------|----------|----------|--------|--------|--------|---------|
| ARCO-10  | TransE   | 914.077  | 0.200 | 0.010 | 0.414 | 0.514  |
| ARCO-10  | RotatE   | 428.235  | 0.759 | 0.680 | 0.845 | 0.867  |
| ARCO-10  | ComplEx  | 1741.747 | 0.192 | 0.131 | 0.258 | 0.308  |
| ARCO-10  | CompGCN  | 359.778  | 0.572 | 0.459 | 0.702 | 0.751  |

### Datasets from `DBPedia`

| Dataset        | Model    | MR      | MRR   | Hits@1 | Hits@5 | Hits@10 |
|----------------|----------|----------|--------|--------|--------|---------|
| DBPEDIA-100K   | TransE   | 3005.94 | 0.114 | 0.012 | 0.219 | 0.294 |
| DBPEDIA-100K   | RotatE   | 2693.98 | 0.371 | 0.282 | 0.468 | 0.541 |
| DBPEDIA-100K   | ComplEx  | 7243.17 | 0.116 | 0.056 | 0.176 | 0.223 |
| DBPEDIA-100K   | CompGCN  | 1659.33 | 0.198 | 0.099 | 0.299 | 0.396 |