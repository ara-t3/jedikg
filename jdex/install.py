
from jdex.cli import CLI
from pathlib import Path
import os
import stat
import shutil
from jdex.owl.reasoning import Reasoner
from jdex.utils.postprocessing import TSVConverter, IDMapper, OWLConverter

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gztar", ".bz2", ".xztar", ".tar.gz", ".tgz"}

def unpack(ui, in_path, out_path, label):
    for zipfile in in_path.iterdir():
        if zipfile.is_file() and zipfile.suffix.lower() in ARCHIVE_EXTENSIONS:
            ui.info(f"Unarchiving {label} {zipfile}")

            shutil.unpack_archive(str(zipfile), str(out_path))
            ui.success(f"{label} saved at {out_path}")
    if (out_path / "__MACOSX").is_dir():
        shutil.rmtree(out_path / "__MACOSX")


def regenerate_knowledge_graph(ui, reasoner, datasets_path: Path | str):
    base_path = Path(datasets_path)

    ui.info(f"Merging Full Knowledge Graph for datasets in {base_path}")

    for data_folder in base_path.iterdir():
        if not data_folder.is_dir():
            continue

        ui.info(f"Merging Knowledge Graph {data_folder.name}")

        reasoner.merging(
            [
                data_folder / "ontology.owl",
                data_folder / "abox" / "individuals.owl",
                data_folder / "abox" / "obj_prop_assertions.nt",
                data_folder / "abox" / "class_assertions.owl"
            ],
            data_folder / "knowledge_graph.owl",
            verbose=0
        )

        ui.success(f"Merged Knowledge Graph files into {data_folder / "knowledge_graph.owl"}")

def regenerate_triples(ui, datasets_path: Path | str):
    base_path = Path(datasets_path)

    ui.info(f"Merging Object Assertions for datasets in {base_path}")

    for data_folder in base_path.iterdir():
        if not data_folder.is_dir():
            continue

        ui.info(f"Merging dataset {data_folder.name}")

        splits_dir = data_folder / "abox" / "splits"
        output_file = data_folder / "abox" / "obj_prop_assertions.nt"
        nt_files = sorted(splits_dir.glob("*.nt"))

        with open(output_file.absolute(), "w") as outfile:
            for nt_file in nt_files:
                with nt_file.open("r", encoding="utf-8") as infile:
                    shutil.copyfileobj(infile, outfile)

        ui.success(f"Merged {len(nt_files)} files into {output_file}")

if __name__ == "__main__":
    cwd = Path.cwd()
    ui = CLI(verbose=1)
    ui.logo("KG-SaF Installer")
    ui.rule("Installation Process")
    ui.subrule("Unpacking Reasoners")
    
    unpack(ui, cwd / "reasoners", cwd / "reasoners" / "unpack", "Reasoners")

    files = [
        cwd / "reasoners/unpack/konclude/Konclude.sh",
        cwd / "reasoners/unpack/konclude/Konclude",
        cwd / "reasoners/unpack/konclude/Binaries/Konclude",
        cwd / "reasoners/unpack/pellet/cli/target/pelletcli/bin/pellet",
    ]

    for file in files:
        ui.info(f"Making Executable Reasoner {file} ")
        os.chmod(file, os.stat(file).st_mode | stat.S_IEXEC)

    if ui.confirm("Do you want to also unpack already available datasets?"):
        ui.subrule("Unarchive Datasets")
        unpack(ui, cwd / "jdset/datasets", cwd / "jdset/datasets" / "unpack", "Dataset")
        ui.subrule("Unarchive Facts")
        unpack(ui, cwd / "jdset/facts", cwd / "jdset/facts" / "unpack", "Facts")
        ui.subrule("Unarchive Schemas")
        unpack(ui, cwd / "jdset/schemas", cwd / "jdset/schemas" / "unpack", "Schemas")

        ui.subrule("Object Property Assertions Triples Reconstruction")
        regenerate_triples(ui, cwd / "jdset/datasets/unpack")


        ui.subrule("Full Knowledge Graph Merging")
        ui.warning("This step will take a lot of time")
        if ui.confirm("Do you want to proceed?"):
            java_11_path = ui.input("Insert JAVA 11 Home Path", default="/opt/homebrew/opt/openjdk@11/")
            max_ram = int(ui.input("Insert Max RAM Threshold for Reasoner", default="8"))
            reasoner = Reasoner(cwd / "reasoners/unpack", java8_path="", java11_path=java_11_path, java_max_ram=max_ram)
            regenerate_knowledge_graph(ui, reasoner, cwd / "jdset/datasets/unpack")

        ui.success("Installation Terminated")
        if ui.confirm("Do you want to run the Post Processing Utility?"):

            ui.logo("Post Processing Utility")

            while True: 
                c = ui.choose("What do you want to run?", [
                    "ID Mappings: Object Properties, Individuals and Classes",
                    "TSV Conversion (PyKEEN / PyTorch Compatibility)",
                    "OWL to JSON Conversion"
                ])

                match c:
                    case "ID Mappings: Object Properties, Individuals and Classes":
                        for data_folder in (cwd / "jdset/datasets/unpack").iterdir():
                            ui.info(f"Computing Mapping for {data_folder}")
                            utility = IDMapper(data_folder)
                            utility.map_to_id()
                            utility.serialize()
                            
                    case "TSV Conversion (PyKEEN / PyTorch Compatibility)":
                        for data_folder in (cwd / "jdset/datasets/unpack").iterdir():
                            ui.info(f"Computing TSV Conversion for {data_folder}")
                            utility = TSVConverter(data_folder)
                            utility.convert()
                            utility.serialize()
                    case "OWL to JSON Conversion":
                        for data_folder in (cwd / "jdset/datasets/unpack").iterdir():
                            ui.info(f"Computing JSON Conversion for {data_folder}")
                            utility = OWLConverter(data_folder)
                            utility.preprocess(verbose=False)
                            utility.serialize()
                    case "Exit":
                        break
    
    ui.rule("Installation Terminated")
