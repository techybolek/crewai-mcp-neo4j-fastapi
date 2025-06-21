// First, show what we're about to delete
MATCH (n)
RETURN labels(n) as NodeTypes, count(n) as Count;

// Show all relationship types
MATCH ()-[r]->()
RETURN type(r) as RelationType, count(r) as Count;

// Delete all relationships first (must be done before deleting nodes)
MATCH ()-[r]->()
DELETE r;

// Delete all nodes
MATCH (n)
DELETE n;

// Verify cleanup
MATCH (n)
RETURN count(n) as RemainingNodes;

MATCH ()-[r]->()
RETURN count(r) as RemainingRelationships; 