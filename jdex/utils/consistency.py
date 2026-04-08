import shutil
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, split_uri

from jdex.cli import CLI
from jdex.owl.reasoning import Reasoner


class InconsistenciesFilterer:
    """Iteratively detect and remove inconsistent assertions from a knowledge graph.

    This class uses an external OWL reasoner (via the ``Reasoner`` abstraction)
    to check ontology consistency and compute justifications for inconsistencies.
    It then removes offending assertions (class assertions and object property
    assertions) until the knowledge graph becomes consistent.

    The filtering process is destructive with respect to the working copy of the
    ontology but preserves the original input file.
    """

    def __init__(self, java_8_path: str, java_11_path: str):
        """Initialize the consistency filterer.

        Args:
            java_8_path (str): Path to a Java 8 installation (required for Pellet justification).
            java_11_path (str): Path to a Java 11 installation (required for ROBOT and related tools).
        """
        self.ui = CLI(verbose=1)
        self.reasoner = Reasoner(
            Path("./reasoners/unpack").absolute(),
            java8_path=java_8_path,
            java11_path=java_11_path,
        )

    def filter_inconsistencies(self, knowledge_graph: str, output_folder: str):
        """Run iterative inconsistency detection and filtering on a knowledge graph.

        The method performs the following steps:

        1. Copies the input ontology to a working file (``fkg.owl``).
        2. Parses and normalizes the ontology serialization.
        3. Repeatedly:
            - Checks consistency using the configured reasoner.
            - If inconsistent, computes a justification.
            - Extracts offending assertions (ClassAssertion and ObjectPropertyAssertion).
            - Removes those assertions from the graph.
        4. Stops when the ontology becomes consistent.
        5. Writes removed triples to a separate file for inspection.

        Args:
            knowledge_graph (str): Path to the input ontology file (.owl).
            output_folder (str): Directory where intermediate and output files will be stored.

        Side Effects:
            - Creates a working ontology file ``fkg.owl`` in the output directory.
            - Writes a justification file ``justification.owl`` during processing.
            - Writes removed triples to ``removed.nt``.
            - Modifies the working ontology until it becomes consistent.
        """

        self.ui.logo(tool_name="JDEX Consistency")
        self.ui.rule("Starting Inconsistency Filtering")

        op = Path(output_folder)
        op.mkdir(parents=False, exist_ok=True)
        kp = op / "fkg.owl"
        shutil.copy(Path(knowledge_graph), kp)

        g = Graph()
        g.parse(kp)
        g.serialize(kp, format="xml")

        out_removed = Graph()
        found = 0
        step = 0

        while True:
            if not self.reasoner.consistency(kp, verbose=0):
                step += 1
                self.ui.warning(
                    f"[Reasoning Step {step}] Knowledge Graph is NOT Consistent: Running Filtering"
                )
                justification = self.reasoner.justification(kp, op / "justification.owl", verbose=0)
                for elem in justification:
                    if "ClassAssertion" in elem:
                        print("FOUND ONE")
                        data = elem.strip("ClassAssertion(").strip(")").split(" ")
                        data = [URIRef(e.strip("<>")) for e in data]
                        triple = (data[1], RDF.type, data[0])
                        if triple in g:
                            out_removed.add(triple)
                            g.remove(triple)
                            found += 1
                            self.ui.success(
                                f"[{found:04d}] Removed <{triple[0]} type {triple[2]}>"
                            )
                    if "ObjectPropertyAssertion" in elem:
                        data = (
                            elem.strip("ObjectPropertyAssertion(").strip(")").split(" ")
                        )
                        data = [URIRef(e.strip("<>")) for e in data]
                        triple = (data[1], data[0], data[2])
                        if triple in g:
                            out_removed.add(triple)
                            g.remove(triple)
                            found += 1
                            self.ui.success(
                                f"[{found:04d}] Removed <{triple[0]} {triple[1]} {triple[2]}>"
                            )
                g.serialize(kp, format="xml")
            else:
                break

        print(f"Found {found} Inconsistencies")
        out_removed.serialize(Path(output_folder) / "removed.nt", format="ntriples")
