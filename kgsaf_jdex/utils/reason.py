#!/usr/bin/env python3
from pathlib import Path
import sys
import subprocess

sys.path.append(str(Path.cwd().parent))



class ReasonerUtility:
    def __init__(self, robot_jar):
        self.robot_jar = robot_jar
        self.base_command =  ["java", "-Xmx20G", "-jar", str(self.robot_jar)]
        


    def check_result(self, result):
        if result.returncode == 0:
            print("Reasoning completed successfully!")
        else:
            print("Reasoning failed with return code:", result.returncode)


    def convert_owl(self, input, output):
        command = self.base_command + [
            "merge",
            "-vvv",
            "--input", str(input),
            "--output", str(output)
        ]
        result = subprocess.run(command, capture_output=False, text=True)
        self.check_result(result)


    
    def filter_unsatisfiable(self, input, output):
        command = self.base_command + [
            "reason",
            "-vvv",
            "--reasoner", "HermiT",
            "--input", str(input),
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        unsatisfiable_classes = []
        for line in result.stdout.split("\n"):
            print(line)
            if 'unsatisfiable:' in line:
                iri = line.split('unsatisfiable:')[1].strip()
                unsatisfiable_classes.append(iri)

        print(unsatisfiable_classes)
    
        if unsatisfiable_classes:
            print(f"Found {len(unsatisfiable_classes)} unsatisfiable classes. Removing them...")
            
            remove_robot = self.base_command + [
                "remove",
                "--input", str(input),
                "--output", str(output)
            ]
            
            # Add each unsatisfiable class as a term to remove
            for iri in unsatisfiable_classes:
                remove_robot.extend(["--term", iri])
        
            # Run the remove command
            remove_result = subprocess.run(remove_robot, capture_output=True, text=True)
            
            if remove_result.returncode == 0:
                print("Successfully removed unsatisfiable classes!")
            else:
                print("Failed to remove classes:", remove_result.stderr)
        else:
            print("No unsatisfiable classes found!")
        
        self.check_result(result)

    def reason(self, axiom_generators, input, output, debug):

        prop_string = ""
        for p in axiom_generators:
            print(f"\t{p}")
            prop_string += " " + p

        command = self.base_command + [
                "reason",
                "-vvv",
                "--reasoner", "HermiT",
                "--input", str(input),
                "--output", str(output),
                "--axiom-generators", prop_string,
                "--remove-redundant-subclass-axioms", "false",
                "--exclude-tautologies", "structural",
                "--include-indirect", "true",
                "-D", str(debug)
        ]

        result = subprocess.run(command, capture_output=False, text=True)
        self.check_result(result)


        
    def serialize(self, graph, output):
        xml_path = output.with_suffix(".xml")
        owl_path = output.with_suffix(".owl")
        graph.serialize(xml_path, format="xml")

        cmd = [
            "java",
            "-Xmx20G",
            "-jar", str(self.robot_jar),
            "merge",
            "--input", str(xml_path),
            "--output", str(owl_path)
        ]
        
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"ROBOT merge failed with return code {result.returncode}")

        xml_path.unlink()
        print(f"Serialized graph saved to {owl_path}")
