from jdex.utils.unpacking import JDEXUnpacker
from jdex.cli import CLI
from pathlib import Path
import os
import stat

if __name__ == "__main__":
    cwd = Path.cwd()
    ui = CLI(verbose=1)
    ui.logo("KG-SaF Installer")
    ui.rule("Installation Process")
    java_11 = ui.input("Enter Java 11 Home")
    unpacker = JDEXUnpacker(java_11_home=java_11)
    ui.subrule("Unpacking Reasoners")
    unpacker._unpack(cwd / "reasoners", cwd / "reasoners" / "unpack", "Reasoners")

    files = [
        cwd / "reasoners/unpack/konclude/Konclude.sh",
        cwd / "reasoners/unpack/konclude/Konclude",
        cwd / "reasoners/unpack/konclude/Binaries/Konclude",
        cwd / "reasoners/unpack/pellet/cli/target/pelletcli/bin/pellet",
    ]

    for file in files:
        ui.info(f"Making Executable Reasoner {file} ")
        os.chmod(file, os.stat(file).st_mode | stat.S_IEXEC)

    unpacker.run()

    ui.rule("Installation Terminated")
