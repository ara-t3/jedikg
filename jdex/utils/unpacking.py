import shutil
from rdflib import Graph
import jdex.utils.conventions.paths as pc
from jdex.utils.conversion import OWLConverter, TSVConverter, IDMapper
import sys
from pathlib import Path
from jdex.cli import CLI
from jdex.owl.reasoning import Reasoner

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gztar", ".bz2", ".xztar", ".tar.gz", ".tgz"}

class JDEXUnpacker:
    def __init__(self, java_11_home: Path, verbose: bool = 1):
        self.reasoner = Reasoner(Path("./reasoners/unpack").absolute(), java11_path=java_11_home, java8_path="")
        self.ui = CLI(verbose)
        self.bp = Path.cwd() / "data" 
        self.verbose = verbose

    def kill(self, code: int = 1):
        self.ui.rule("JDEX Unpacker Terminated")
        sys.exit(code)

    def startup_screen(self):
        self.ui.logo(tool_name="Data Unpacker")

    def run(self):
        self.startup_screen()
        
        while True:
            choice = self.interactive_menu()
            match choice:
                case "Full Suite":
                    self.ui.rule("Full Unpacking Suite")
                    self.ui.subrule("Unpacking Datasets")
                    self._unpack(self.bp / "datasets", self.bp / "datasets" / "unpack", "Dataset")
                    self.ui.subrule("Unpacking Facts")
                    self._unpack(self.bp / "facts", self.bp / "facts" / "unpack", "Facts")
                    self.ui.subrule("Unpacking Schemas")
                    self._unpack(self.bp / "schemas", self.bp / "schemas" / "unpack", "Schemas")
                    self.ui.subrule("Merging Objcect Property Assertions")
                    self.regenerate_triples(self.bp / "datasets/unpack")
                    self.ui.subrule("Merging Full Knowledge Graph")
                    self.regenerate_knowledge_graph(self.bp / "datasets/unpack")
                    self.ui.subrule("Done")
                case "Unpack Everything":
                    self.ui.subrule("Unpacking Everything")
                    self._unpack(self.bp / "datasets", self.bp / "datasets" / "unpack", "Dataset")
                    self._unpack(self.bp / "facts", self.bp / "facts" / "unpack", "Facts")
                    self._unpack(self.bp / "schemas", self.bp / "schemas" / "unpack", "Schemas")
                    self.ui.subrule("Done")
                case "Unpack Facts":
                    self.ui.subrule("Facts Unpacking")
                    self._unpack(self.bp / "facts", self.bp / "facts" / "unpack", "Facts")
                    self.ui.subrule("Done")
                case "Unpack Schemas":
                    self.ui.subrule("Schemas Unpacking")
                    self._unpack(self.bp / "schemas", self.bp / "schemas" / "unpack", "Schemas")
                    self.ui.subrule("Done")
                case "Unpack Datasets":
                    self.ui.subrule("Dataset Unpacking")
                    self._unpack(self.bp / "datasets", self.bp / "datasets" / "unpack", "Dataset")
                    self.ui.subrule("Done")
                case "Regenerate Everything":
                    self.ui.subrule("Full Dataset Regeneration")
                    self.regenerate_triples(self.bp / "datasets/unpack")
                    self.regenerate_knowledge_graph(self.bp / "datasets/unpack")
                    self.ui.subrule("Done")
                case "Regenerate Triples":
                    self.ui.subrule("Full Triples Regeneration")
                    self.regenerate_triples(self.bp / "datasets/unpack")
                    self.ui.subrule("Done")
                case "Regenerate Full Knowledge Graph":
                    self.ui.subrule("Knowledge Graph Regeneration")
                    self.regenerate_knowledge_graph(self.bp / "datasets/unpack")
                    self.ui.subrule("Done")
                case "Exit":
                    self.kill(0)
        

    def interactive_menu(self) -> str:
        return self.ui.choose(
            "What do you want to do?",
            [
                "Full Suite",
                "",
                "Unpack Everything",
                "Unpack Datasets",
                "Unpack Facts",
                "Unpack Schemas",
                "",
                "Regenerate Everything", 
                "Regenerate Triples",
                "Regenerate Full Knowledge Graph",
                "",
                "Exit"
            ],
        )
    
    def regenerate_knowledge_graph(self, datasets_path: Path | str):
        base_path = Path(datasets_path)

        self.ui.info(f"Merging Full Knowledge Graph for datasets in {base_path}")

        for data_folder in base_path.iterdir():
            if not data_folder.is_dir():
                continue

            self.ui.info(f"Merging Knowledge Graph {data_folder.name}")

            self.reasoner.merging(
                [
                    data_folder / "ontology.owl",
                    data_folder / "abox" / "individuals.owl",
                    data_folder / "abox" / "obj_prop_assertions.nt",
                    data_folder / "abox" / "class_assertions.owl"
                ],
                data_folder / "knowledge_graph.owl",
                verbose=self.verbose
            )

            self.ui.success(f"Merged Knowledge Graph files into {data_folder / "knowledge_graph.owl"}")

    def regenerate_triples(self, datasets_path: Path | str):
        base_path = Path(datasets_path)

        self.ui.info(f"Merging Object Assertions for datasets in {base_path}")

        for data_folder in base_path.iterdir():
            if not data_folder.is_dir():
                continue

            self.ui.info(f"Merging dataset {data_folder.name}")

            splits_dir = data_folder / "abox" / "splits"
            output_file = data_folder / "abox" / "obj_prop_assertions.nt"
            nt_files = sorted(splits_dir.glob("*.nt"))

            with open(output_file.absolute(), "w") as outfile:
                for nt_file in nt_files:
                    with nt_file.open("r", encoding="utf-8") as infile:
                        shutil.copyfileobj(infile, outfile)

            self.ui.success(f"Merged {len(nt_files)} files into {output_file}")



    def _unpack(self, in_path, out_path, label):
        for zipfile in in_path.iterdir():
            if zipfile.is_file() and zipfile.suffix.lower() in ARCHIVE_EXTENSIONS:
                self.ui.info(f"Unpacking {label} {zipfile}")

                shutil.unpack_archive(str(zipfile), str(out_path))
                self.ui.success(f"{label} saved at {out_path}")
                




if __name__ == "__main__":
    unpacker = JDEXUnpacker(verbose=1, java_11_home="/opt/homebrew/opt/openjdk@11/")
    unpacker.run()


