from kgsaf_jdex.jdex import JDEX
    

if __name__ == "__main__":
    configuration = {
        "dataset_name": "TEST",
        "paths": {
            "schema": "schema.owl",
            "data": "data/",
            "output": "output/",
        },
        "reasoning": {
            "enabled": True,
            "java_8_home": "/usr/lib/jvm/java-8",
            "java_11_home": "/usr/lib/jvm/java-11",
            "materialization": {
                "enabled": True,
                "axioms": [
                    "SubClass",
                    "EquivalentClass",
                ],
            },
            "realization": {
                "enabled": True,
            },
            "modularization": {
                "enabled": True,
            },
        },
        "test_leakage_filtering": {
            "enabled": True,
        },
        "split": {
            "enabled": True,
            "train_percent": 80,
            "validation_percent": 10,
            "test_percent": 10,
            "transductive": True,
        },
        "description_logic_profile": "EL",
        "post_processing": {
            "json_conversion": True,
            "id_mapping": True,
        },
    }

    jdex = JDEX.from_dict(configuration)
    print(jdex.config_summary())

