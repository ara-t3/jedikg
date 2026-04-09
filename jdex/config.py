from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from jdex.owl.reasoning import PresetAxioms


DLProfile = Literal["EL", "ALC", None]

@dataclass
class PathsConfig:
    """Configuration for dataset input/output paths.

    Attributes:
        schema (Path): Path to the ontology/schema file.
        data (Path): Path to the dataset/triples file.
        output (Path): Directory where processed outputs will be stored.
    """

    schema: Path
    data: Path
    output: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PathsConfig":
        """Create a PathsConfig instance from a dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing path definitions.

        Returns:
            PathsConfig: Initialized PathsConfig instance.
        """
        return cls(
            schema=Path(data["schema"]),
            data=Path(data["data"]),
            output=Path(data["output"]),
        )


@dataclass
class MaterializationConfig:
    """Configuration for TBox materialization reasoning.

    Attributes:
        enabled (bool): Whether materialization is enabled.
        axioms (list[str]): List of axioms to materialize.
        reasoner (str): Reasoner used for materialization ("hermit" or "elk").

    Raises:
        ValueError: If unsupported axioms or reasoner are provided.
    """

    enabled: bool = True
    axioms: list[str] = field(default_factory=PresetAxioms.tbox_materialization)
    reasoner: str = "hermit"

    def __post_init__(self) -> None:
        """Validate axioms and reasoner."""
        allowed_axioms = set(PresetAxioms.tbox_materialization())
        invalid_axioms = [axiom for axiom in self.axioms if axiom not in allowed_axioms]
        if invalid_axioms:
            raise ValueError(
                f"Unsupported axioms: {invalid_axioms}. "
                f"Allowed axioms are: {sorted(allowed_axioms)}"
            )

        allowed_reasoners = ["hermit", "elk"]
        if self.reasoner not in allowed_reasoners:
            raise ValueError(f"Unsupported reasoner {self.reasoner}")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "MaterializationConfig":
        """Create a MaterializationConfig from a dictionary.

        Args:
            data (dict[str, Any] | None): Configuration dictionary.

        Returns:
            MaterializationConfig: Initialized instance.
        """
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            axioms=list(data.get("axioms", PresetAxioms.tbox_materialization())),
            reasoner=data.get("reasoner", "hermit"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "MaterializationConfig":
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            axioms=list(data.get("axioms", PresetAxioms.tbox_materialization())),
            reasoner=data.get("reasoner", "hermit")
        )


@dataclass
class RealizationConfig:
    """Configuration for realization reasoning.

    Attributes:
        enabled (bool): Whether realization is enabled.
        reasoner (str): Reasoner used ("hermit", "konclude", or "elk").

    Raises:
        ValueError: If an unsupported reasoner is provided.
    """

    enabled: bool = True
    reasoner: str = "konclude"

    def __post_init__(self) -> None:
        """Validate reasoner."""
        allowed_reasoners = ["hermit", "konclude", "elk"]
        if self.reasoner not in allowed_reasoners:
            raise ValueError(f"Unsupported reasoner {self.reasoner}")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "RealizationConfig":
        """Create a RealizationConfig from a dictionary.

        Args:
            data (dict[str, Any] | None): Configuration dictionary.

        Returns:
            RealizationConfig: Initialized instance.
        """
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            reasoner=data.get("reasoner", "konclude"),
        )
    

@dataclass
class ModularizationConfig:
    """Configuration for ontology modularization.

    Attributes:
        enabled (bool): Whether modularization is enabled.
    """

    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ModularizationConfig":
        """Create a ModularizationConfig from a dictionary."""
        data = data or {}
        return cls(enabled=data.get("enabled", True))
    

@dataclass
class ConsistencyConfig:
    """Configuration for consistency checking.

    Attributes:
        convert_ntriples (bool): Whether to convert data to N-Triples before checking.
    """

    convert_ntriples: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ConsistencyConfig":
        """Create a ConsistencyConfig from a dictionary."""
        data = data or {}
        return cls(convert_ntriples=data.get("convert_ntriples", False))
    

@dataclass
class DecompositionConfig:
    """Configuration for ontology decomposition.

    Attributes:
        tbox (bool): Whether to decompose the TBox.
        rbox (bool): Whether to decompose the RBox.
    """

    tbox: bool = True
    rbox: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DecompositionConfig":
        """Create a DecompositionConfig from a dictionary."""
        data = data or {}
        return cls(
            rbox=data.get("rbox", True),
            tbox=data.get("tbox", True),
        )

@dataclass
class SatisfiabilityConfig:
    """Configuration for satisfiability checking.

    Attributes:
        filter_unsatisfiable (bool): Whether to remove unsatisfiable entities.
        reasoner (str): Reasoner used ("hermit" or "elk").

    Raises:
        ValueError: If an unsupported reasoner is provided.
    """

    filter_unsatisfiable: bool = False
    reasoner: str = "hermit"

    def __post_init__(self) -> None:
        """Validate reasoner."""
        allowed_reasoners = ["hermit", "elk"]
        if self.reasoner not in allowed_reasoners:
            raise ValueError(f"Unsupported reasoner {self.reasoner}")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SatisfiabilityConfig":
        """Create a SatisfiabilityConfig from a dictionary."""
        data = data or {}
        return cls(
            filter_unsatisfiable=data.get("filter_unsatisfiable", False),
            reasoner=data.get("reasoner", "hermit"),
        )
    

@dataclass
class ReasoningConfig:
    """Configuration for all reasoning services.

    Attributes:
        java_8_home (str | None): Path to Java 8 installation.
        java_11_home (str | None): Path to Java 11 installation.
        java_max_ram (int): Maximum RAM (GB) allocated to Java.
        satisfiability (SatisfiabilityConfig): Satisfiability settings.
        materialization (MaterializationConfig): Materialization settings.
        realization (RealizationConfig): Realization settings.
        modularization (ModularizationConfig): Modularization settings.
        decomposition (DecompositionConfig): Decomposition settings.
        consistency (ConsistencyConfig): Consistency settings.
    """

    java_8_home: str | None = None
    java_11_home: str | None = None
    java_max_ram: int = 4
    satisfiability: SatisfiabilityConfig = field(default_factory=SatisfiabilityConfig)
    materialization: MaterializationConfig = field(default_factory=MaterializationConfig)
    realization: RealizationConfig = field(default_factory=RealizationConfig)
    modularization: ModularizationConfig = field(default_factory=ModularizationConfig)
    decomposition: DecompositionConfig = field(default_factory=DecompositionConfig)
    consistency: ConsistencyConfig = field(default_factory=ConsistencyConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ReasoningConfig":
        """Create a ReasoningConfig from a dictionary."""
        data = data or {}
        return cls(
            java_max_ram=data.get("java_max_ram", 4),
            java_8_home=data["java_8_home"] if data.get("java_8_home") else None,
            java_11_home=data["java_11_home"] if data.get("java_11_home") else None,
            materialization=MaterializationConfig.from_dict(data.get("materialization")),
            realization=RealizationConfig.from_dict(data.get("realization")),
            modularization=ModularizationConfig.from_dict(data.get("modularization")),
            decomposition=DecompositionConfig.from_dict(data.get("decomposition")),
            consistency=ConsistencyConfig.from_dict(data.get("consistency")),
            satisfiability=SatisfiabilityConfig.from_dict(data.get("satisfiability")),
        )

@dataclass
class TestLeakageFilteringConfig:
    """Configuration for test leakage filtering.

    Attributes:
        enabled (bool): Whether filtering is enabled.
        minimum_frequency (float): Threshold for filtering leakage.
    """

    enabled: bool = True
    minimum_frequency: float = 0.97

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "TestLeakageFilteringConfig":
        """Create a TestLeakageFilteringConfig from a dictionary."""
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            minimum_frequency=data.get("minimum_frequency", 0.97),
        )

@dataclass
class SplitConfig:
    """Configuration for dataset splitting.

    Attributes:
        enabled (bool): Whether splitting is enabled.
        train_percent (int): Percentage of training data.
        validation_percent (int): Percentage of validation data.
        test_percent (int): Percentage of test data.
        transductive (bool): Whether to use transductive splitting.
        test_leakage_filtering (TestLeakageFilteringConfig): Leakage filtering settings.

    Raises:
        ValueError: If percentages do not sum to 100 when enabled.
    """

    enabled: bool = True
    train_percent: int = 80
    validation_percent: int = 10
    test_percent: int = 10
    transductive: bool = True
    test_leakage_filtering: TestLeakageFilteringConfig = field(default_factory=TestLeakageFilteringConfig)

    def __post_init__(self) -> None:
        """Validate split percentages."""
        if self.enabled:
            total = self.train_percent + self.validation_percent + self.test_percent
            if total != 100:
                raise ValueError(f"Split percentages must sum to 100, got {total}.")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SplitConfig":
        """Create a SplitConfig from a dictionary."""
        data = data or {}
        return cls(
            enabled=data.get("enabled", True),
            train_percent=data.get("train_percent", 80),
            validation_percent=data.get("validation_percent", 10),
            test_percent=data.get("test_percent", 10),
            transductive=data.get("transductive", True),
            test_leakage_filtering=TestLeakageFilteringConfig.from_dict(
                data.get("test_leakage_filtering")
            ),
        )


@dataclass
class PostProcessingConfig:
    """Configuration for post-processing steps.

    Attributes:
        json_conversion (bool): Whether to export JSON files.
        id_mapping (bool): Whether to generate ID mappings.
        tsv_conversion (bool): Whether to export TSV files.
    """

    json_conversion: bool = True
    id_mapping: bool = True
    tsv_conversion: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PostProcessingConfig":
        """Create a PostProcessingConfig from a dictionary."""
        data = data or {}
        return cls(
            json_conversion=data.get("json_conversion", True),
            id_mapping=data.get("id_mapping", True),
            tsv_conversion=data.get("tsv_conversion", True),
        )


@dataclass
class JDEXConfig:
    """Top-level configuration for JDEX pipeline.

    Attributes:
        dataset_name (str): Name of the dataset.
        paths (PathsConfig): Input/output paths configuration.
        verbose (int): Verbosity level.
        interactive_shell (bool): Whether to enable interactive mode.
        reasoning (ReasoningConfig): Reasoning configuration.
        test_leakage_filtering (TestLeakageFilteringConfig): Global leakage filtering.
        split (SplitConfig): Dataset splitting configuration.
        description_logic_profile (DLProfile): DL profile ("EL", "ALC", "SROIQ", or None).
        post_processing (PostProcessingConfig): Post-processing configuration.

    Raises:
        ValueError: If an invalid description logic profile is provided.
    """

    dataset_name: str
    paths: PathsConfig
    verbose: int = 1
    interactive_shell: bool = True
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    test_leakage_filtering: TestLeakageFilteringConfig = field(default_factory=TestLeakageFilteringConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    description_logic_profile: DLProfile = None
    post_processing: PostProcessingConfig = field(default_factory=PostProcessingConfig)

    def __post_init__(self) -> None:
        """Validate description logic profile."""
        allowed_profiles = {"EL", "ALC", None}
        if self.description_logic_profile:
            if self.description_logic_profile not in allowed_profiles:
                raise ValueError(
                    "description_logic_profile must be one of: "
                    "'EL', 'ALC', 'SROIQ', or None."
                )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JDEXConfig":
        """Create a JDEXConfig from a dictionary.

        Args:
            data (dict[str, Any]): Configuration dictionary.

        Returns:
            JDEXConfig: Initialized configuration object.
        """
        return cls(
            dataset_name=data["dataset_name"],
            verbose=data.get("verbose", 1),
            interactive_shell=data.get("interactive_shell", True),
            paths=PathsConfig.from_dict(data["paths"]),
            reasoning=ReasoningConfig.from_dict(data.get("reasoning")),
            test_leakage_filtering=TestLeakageFilteringConfig.from_dict(
                data.get("test_leakage_filtering")
            ),
            split=SplitConfig.from_dict(data.get("split")),
            description_logic_profile=data.get("description_logic_profile"),
            post_processing=PostProcessingConfig.from_dict(
                data.get("post_processing")
            ),
        )

    def pretty_print(self) -> str:
        """Return a formatted string summarizing the configuration.

        Returns:
            str: Human-readable configuration summary.
        """
        return f"""
JDEX Configuration Summary
--------------------------

GENERAL SETTINGS

dataset_name: {self.dataset_name}
verbose: {self.verbose}
interactive_shell: {self.interactive_shell}

PATHS SETTINGS

schema: {self.paths.schema}
data: {self.paths.data}
output: {self.paths.output}

REASONING SERVICES SETTINGS

java_8_home: {self.reasoning.java_8_home}
java_11_home: {self.reasoning.java_11_home}
java_max_ram: {self.reasoning.java_max_ram}

consistency:
    convert_ntriples: {self.reasoning.consistency.convert_ntriples}

satisfiability:
    filter_unsatisfiable: {self.reasoning.satisfiability.filter_unsatisfiable}
    reasoner: {self.reasoning.satisfiability.reasoner}

materialization:
    enabled: {self.reasoning.materialization.enabled}
    axioms: {self.reasoning.materialization.axioms}
    reasoner: {self.reasoning.materialization.reasoner}

realization:
    enabled: {self.reasoning.realization.enabled}
    reasoner: {self.reasoning.realization.reasoner}

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
    tsv_conversion: {self.post_processing.tsv_conversion}
            """.strip()


