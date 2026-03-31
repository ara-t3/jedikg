from rdflib import URIRef, RDF, RDFS, OWL, XSD

BUILTIN_URIS = {

    # =====================
    # RDF core
    # =====================
    RDF.type,
    RDF.Property,
    RDF.Statement,
    RDF.subject,
    RDF.predicate,
    RDF.object,

    RDF.List,
    RDF.first,
    RDF.rest,
    RDF.nil,

    # =====================
    # RDFS
    # =====================
    RDFS.Resource,
    RDFS.Class,
    RDFS.Literal,
    RDFS.Container,
    RDFS.ContainerMembershipProperty,

    RDFS.subClassOf,
    RDFS.subPropertyOf,
    RDFS.domain,
    RDFS.range,
    RDFS.label,
    RDFS.comment,
    RDFS.isDefinedBy,
    RDFS.seeAlso,
    RDFS.member,

    # =====================
    # OWL core classes
    # =====================
    OWL.Thing,
    OWL.Nothing,
    OWL.Class,
    OWL.Restriction,
    OWL.NamedIndividual,
    OWL.Axiom,

    # =====================
    # OWL properties (types)
    # =====================
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.AnnotationProperty,

    OWL.topObjectProperty,
    OWL.bottomObjectProperty,
    OWL.topDataProperty,
    OWL.bottomDataProperty,

    # =====================
    # OWL property characteristics
    # =====================
    OWL.FunctionalProperty,
    OWL.InverseFunctionalProperty,
    OWL.TransitiveProperty,
    OWL.SymmetricProperty,
    OWL.AsymmetricProperty,
    OWL.ReflexiveProperty,
    OWL.IrreflexiveProperty,

    # =====================
    # OWL logical axioms
    # =====================
    OWL.equivalentClass,
    OWL.equivalentProperty,
    OWL.disjointWith,
    OWL.disjointUnionOf,
    OWL.sameAs,
    OWL.differentFrom,
    OWL.inverseOf,

    # Property chains
    OWL.propertyChainAxiom,

    # =====================
    # OWL class expressions
    # =====================
    OWL.intersectionOf,
    OWL.unionOf,
    OWL.complementOf,
    OWL.oneOf,

    # =====================
    # OWL restrictions – values
    # =====================
    OWL.onProperty,
    OWL.allValuesFrom,
    OWL.someValuesFrom,
    OWL.hasValue,
    OWL.hasSelf,

    # =====================
    # OWL cardinalities (OWL 1)
    # =====================
    OWL.cardinality,
    OWL.minCardinality,
    OWL.maxCardinality,

    # =====================
    # OWL qualified cardinalities (OWL 2)
    # =====================
    OWL.qualifiedCardinality,
    OWL.minQualifiedCardinality,
    OWL.maxQualifiedCardinality,
    OWL.onClass,
    OWL.onDataRange,

    # =====================
    # OWL annotations
    # =====================
    OWL.versionInfo,
    OWL.priorVersion,
    OWL.backwardCompatibleWith,
    OWL.incompatibleWith,

    # =====================
    # Datatypes
    # =====================
    XSD.string,
    XSD.integer,
    XSD.boolean,
    XSD.decimal,
    XSD.date,
    XSD.dateTime,


    # =====================
    # Other
    # =====================
    URIRef("http://www.w3.org/ns/prov#wasInfluencedBy"),
    URIRef("http://www.w3.org/ns/prov#wasDerivedFrom"),
    URIRef("http://schema.org/Thing"),
    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Resource")
}
