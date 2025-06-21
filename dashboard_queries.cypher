// View entire graph
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m;

// View Staff and their relationships
MATCH (s:Staff)
OPTIONAL MATCH (s)-[r]->(m)
RETURN s, r, m;

// View Order flow
MATCH (p:Person)-[:MADE]->(o:Order)-[r]->(n)
RETURN p, o, r, n;

// View Product supply chain
MATCH (v:Vendor)-[:SUPPLIES]->(p:Product)<-[:CONTAINS]-(o:Order)
RETURN v, p, o;

// View Documentation trail
MATCH (s:Staff)-[:WROTE]->(d:Doc)-[:ABOUT]->(p:Product)
RETURN s, d, p;

// View Delivery management
MATCH (s:Staff)-[:MANAGES]->(d:Delivery)<-[:DELIVERED_BY]-(o:Order)
RETURN s, d, o;

// View Company structure
MATCH (n)-[:WORKS_FOR]->(c:Company)
RETURN n, c;

// Get a summary of all relationships
MATCH ()-[r]->()
RETURN type(r) as RelationType, count(r) as Count
ORDER BY Count DESC; 