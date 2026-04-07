import shutil
from rdflib import Graph
import jdex.utils.conventions.paths as pc
from jdex.utils.conversion import OWLConverter, TSVConverter, IDMapper
import sys
from pathlib import Path
from jdex.cli import CLI

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gztar", ".bz2", ".xztar", ".tar.gz", ".tgz"}

class JDEXUnpacker:
    def __init__(self, verbose: bool = 1):
        self.ui = CLI(verbose)
        self.bp = Path.cwd() / "data" 

    def kill(self, code: int = 1):
        self.ui.rule("JDEX Unpacker Terminated")
        sys.exit(code)

    def startup_screen(self):
        self.ui.logo(tool_name="JDEX Unpacker")

    def run(self):
        self.startup_screen()
        
        while True:
            choice = self.interactive_menu()
            match choice:
                case "Unpack Everything":
                    self.ui.subrule("Unpacking Everything")
                    self.unpack_datasets(self.bp / "datasets")
                    self.unpack_facts(self.bp / "facts")
                    self.unpack_schemas(self.bp / "schemas")
                    self.ui.subrule("Done")
                case "Unpack Facts":
                    self.ui.subrule("Dataset Unpacking")
                    self.unpack_facts(self.bp / "facts")
                    self.ui.subrule("Done")
                case "Unpack Schemas":
                    self.ui.subrule("Dataset Unpacking")
                    self.unpack_schemas(self.bp / "schemas")
                    self.ui.subrule("Done")
                case "Unpack Datasets":
                    self.ui.subrule("Dataset Unpacking")
                    self.unpack_datasets(self.bp / "datasets")
                    self.ui.subrule("Done")
                case "Exit":
                    self.kill(0)
        

    def interactive_menu(self) -> str:
        return self.ui.choose(
            "What do you want to do?",
            [
                "Unpack Everything",
                "Unpack Datasets",
                "Unpack Facts",
                "Unpack Schemas",
                "Exit"
            ],
        )
    
    def unpack_datasets(self, datasets_path: Path | str):
        inp = Path(datasets_path)
        outp = inp / "unpack"

        for zipfile in inp.iterdir():
            if zipfile.is_file() and zipfile.suffix.lower() in ARCHIVE_EXTENSIONS:
                self.ui.info(f"Unpacking Dataset {zipfile}")
                out_folder = outp / zipfile.stem

                if out_folder.exists():
                    shutil.rmtree(out_folder)

                shutil.unpack_archive(str(zipfile), str(out_folder))
                self.ui.success(f"Dataset saved at {out_folder}")


    def unpack_schemas(self, schemas_path: Path | str):
        inp = Path(schemas_path)
        outp = inp / "unpack"

        for zipfile in inp.iterdir():
            if zipfile.is_file() and zipfile.suffix.lower() in ARCHIVE_EXTENSIONS:
                self.ui.info(f"Unpacking Schema {zipfile}")
                out_folder = outp / zipfile.stem

                if out_folder.exists():
                    shutil.rmtree(out_folder)

                shutil.unpack_archive(str(zipfile), str(out_folder))
                self.ui.success(f"Schema saved at {out_folder}")


    def unpack_facts(self, facts_path: Path | str):
        inp = Path(facts_path)
        outp = inp / "unpack"

        for zipfile in inp.iterdir():
            if zipfile.is_file() and zipfile.suffix.lower() in ARCHIVE_EXTENSIONS:
                self.ui.info(f"Unpacking Facts {zipfile}")
                out_folder = outp 

                shutil.unpack_archive(str(zipfile), str(out_folder))
                self.ui.success(f"Facts saved at {out_folder}")


if __name__ == "__main__":
    unpacker = JDEXUnpacker(verbose=1)
    unpacker.run()


