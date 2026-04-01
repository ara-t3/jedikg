for d in */; do
  zip -r "${d%/}.zip" "$d" \
    -x "*/abox/obj_prop_assertions.nt" \
    -x "*/knowledge_graph.owl"
done