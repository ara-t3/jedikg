from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from kgsaf.tools.reasoner import PresetAxioms


DLProfile = Literal["EL", "ALC", "SROIQ", None]

@dataclass
class PathsConfig:
    schema: Path
    data: Path
    output: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PathsConfig":
        return cls(
            schema=Path(data["schema"]),
            data=Path(data["data"]),
            output=Path(data["output"]),
        )


@dataclass
class MaterializationConfig:
    enabled: bool = True
    axioms: list[str] = field(default_factory=PresetAxioms.tbox_materialization)

    def __post_init__(self) -> None:
        allowed_axioms = set(PresetAxioms.tbox_materialization())
        invalid_axioms = [axiom for axiom in self.axioms if axiom not in allowed_axioms]
        if invalid_axioms:
            raise ValueError(
                f"Unsupported axioms: {invalid_axioms}. "
                f"Allowed axioms are: {sorted(allowed_axioms)}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "MaterializationConfig":
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            axioms=list(data.get("axioms", PresetAxioms.tbox_materialization())),
        )


@dataclass
class RealizationConfig:
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "RealizationConfig":
        data = data or {}
        return cls(enabled=data.get("enabled", True))


@dataclass
class ModularizationConfig:
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ModularizationConfig":
        data = data or {}
        return cls(enabled=data.get("enabled", True))
    

@dataclass
class DecompositionConfig:
    tbox: bool = True
    rbox: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ModularizationConfig":
        data = data or {}
        return cls(rbox=data.get("rbox", True), tbox=data.get("tbox", True))


@dataclass
class ReasoningConfig:
    java_8_home: str | None = None
    java_11_home: str | None = None
    java_max_ram: int = 4
    filter_unsatisfiable: bool = True
    materialization: MaterializationConfig = field(default_factory=MaterializationConfig)
    realization: RealizationConfig = field(default_factory=RealizationConfig)
    modularization: ModularizationConfig = field(default_factory=ModularizationConfig)
    decomposition: DecompositionConfig = field(default_factory=DecompositionConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ReasoningConfig":
        data = data or {}
        return cls(
            java_max_ram = data.get("java_max_ram", 4),
            filter_unsatisfiable = data.get("filter_unsatisfiable", True),
            java_8_home= data["java_8_home"] if data.get("java_8_home") else None,
            java_11_home=data["java_11_home"] if data.get("java_11_home") else None,
            materialization=MaterializationConfig.from_dict(data.get("materialization")),
            realization=RealizationConfig.from_dict(data.get("realization")),
            modularization=ModularizationConfig.from_dict(data.get("modularization")),
            decomposition=DecompositionConfig.from_dict(data.get("decomposition"))
        )


@dataclass
class TestLeakageFilteringConfig:
    enabled: bool = True
    minimum_frequency: float = 0.97

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "TestLeakageFilteringConfig":
        data = data or {}
        return cls(enabled=data.get("enabled", True), minimum_frequency=data.get("minimum_frequency", 0.97))


@dataclass
class SplitConfig:
    enabled: bool = True
    train_percent: int = 80
    validation_percent: int = 10
    test_percent: int = 10
    transductive: bool = True
    test_leakage_filtering : TestLeakageFilteringConfig = field(default_factory=TestLeakageFilteringConfig)

    def __post_init__(self) -> None:
        if self.enabled:
            total = self.train_percent + self.validation_percent + self.test_percent
            if total != 100:
                raise ValueError(
                    f"Split percentages must sum to 100, got {total}."
                )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SplitConfig":
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            train_percent=data.get("train_percent", 80),
            validation_percent=data.get("validation_percent", 10),
            test_percent=data.get("test_percent", 10),
            transductive=data.get("transductive", True),
            test_leakage_filtering = TestLeakageFilteringConfig.from_dict(data.get("test_leakage_filtering"))
        )


@dataclass
class PostProcessingConfig:
    json_conversion: bool = True
    id_mapping: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PostProcessingConfig":
        data = data or {}
        return cls(
            json_conversion=data.get("json_conversion", True),
            id_mapping=data.get("id_mapping", True),
        )


@dataclass
class JDEXConfig:
    dataset_name: str
    paths: PathsConfig
    verbose: int = 1
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    test_leakage_filtering: TestLeakageFilteringConfig = field(default_factory=TestLeakageFilteringConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    description_logic_profile: DLProfile = None
    post_processing: PostProcessingConfig = field(default_factory=PostProcessingConfig)

    def __post_init__(self) -> None:
        allowed_profiles = {"EL", "ALC", "SROIQ", None}
        if self.description_logic_profile not in allowed_profiles:
            raise ValueError(
                "description_logic_profile must be one of: 'EL', 'ALC', 'SROIQ', or None."
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JDEXConfig":
        return cls(
            dataset_name=data["dataset_name"],
            verbose=data.get("verbose", 1),
            paths=PathsConfig.from_dict(data["paths"]),
            reasoning=ReasoningConfig.from_dict(data.get("reasoning")),
            test_leakage_filtering=TestLeakageFilteringConfig.from_dict(
                data.get("test_leakage_filtering")
            ),
            split=SplitConfig.from_dict(data.get("split")),
            description_logic_profile=data.get("description_logic_profile"),
            post_processing=PostProcessingConfig.from_dict(data.get("post_processing")),
        )



    def pretty_print(self) -> str:
        return f"""
JDEX Configuration Summary
--------------------------

GENERAL SETTINGS

dataset_name: {self.dataset_name}
verbose: {self.verbose}

PATHS SETTINGS

schema: {self.paths.schema}
data: {self.paths.data}
output: {self.paths.output}

REASONING SERVICES SETTINGS

java_8_home: {self.reasoning.java_8_home}
java_11_home: {self.reasoning.java_11_home}
java_max_ram: {self.reasoning.java_max_ram}
filter_unsatisfiable: {self.reasoning.filter_unsatisfiable}

materialization:
    enabled: {self.reasoning.materialization.enabled}
    axioms: {self.reasoning.materialization.axioms}

realization:
    enabled: {self.reasoning.realization.enabled}

modularization:
    enabled: {self.reasoning.modularization.enabled}

decomposition:
    tbox: {self.reasoning.decomposition.tbox}
    rbox: {self.reasoning.decomposition.rbox}

description_logic_profile: {self.description_logic_profile}

MACHINE LEARNING SETTINGS



split:
    enabled: {self.split.enabled}
    train_percent: {self.split.train_percent}
    validation_percent: {self.split.validation_percent}
    test_percent: {self.split.test_percent}
    transductive: {self.split.transductive}
    test_leakage_filtering:
        enabled: {self.split.test_leakage_filtering.enabled}
        minimum_frequency: {self.split.test_leakage_filtering.minimum_frequency}

post_processing:
    json_conversion: {self.post_processing.json_conversion}
    id_mapping: {self.post_processing.id_mapping}
            """.strip()


