from jdex.owl.reasoning import Reasoner
from pathlib import Path
import shutil
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

class ConsistencyFilterer:
    def __init__(self, java_8_path: str, java_11_path: str):
        self.reasoner = Reasoner(Path("./reasoners/unpack").absolute(), java8_path=java_8_path, java11_path=java_11_path)

    def filter_inconsistencies(self, knowledge_graph: str, output_folder: str):
        op = Path(output_folder)
        op.mkdir(parents=False, exist_ok=True)
        kp =  op / "fix.owl"
        shutil.copy(Path(knowledge_graph), kp)

        g = Graph()
        g.parse(kp)
        g.serialize(kp, format="xml")

        out_removed = Graph()
        found = 0

        while True:
            if not self.reasoner.consistency(kp):
                justification = self.reasoner.justification(kp, op / "j.owl")
                for elem in justification:
                    if "ClassAssertion" in elem:
                        data = elem.strip("ClassAssertion(").strip(")").split(" ")
                        data = [URIRef(e.strip("<>")) for e in data]
                        triple = (data[1], RDF.type, data[0])
                        if triple in g:
                            out_removed.add(triple)
                            g.remove(triple)
                            found += 1
                            print(f"[{found:03d}] Removed {triple}")
                    if "ObjectPropertyAssertion" in elem:
                        data = elem.strip("ObjectPropertyAssertion(").strip(")").split(" ")
                        data = [URIRef(e.strip("<>")) for e in data]
                        triple = (data[1], data[0], data[2])
                        if triple in g:
                            out_removed.add(triple)
                            g.remove(triple)
                            found += 1
                            print(f"[{found:03d}] Removed {triple}")
                g.serialize(kp, format="xml")
            else:
                break

        print(f"Found {found} Inconsistencies")
        out_removed.serialize(Path(output_folder) / "removed.nt", format="ntriples")



if __name__ == "__main__":
    filter = ConsistencyFilterer(
        java_8_path="/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home",
        java_11_path="/opt/homebrew/opt/openjdk@11/")
    
    filter.filter_inconsistencies(
        "/Users/navis/dev/projects/kg-saf/test/TEST_CONST/kg_100k.owl",
        "/Users/navis/dev/projects/kg-saf/test/TEST_CONST/"
    )

