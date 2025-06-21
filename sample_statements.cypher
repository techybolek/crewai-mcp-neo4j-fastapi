// Count all nodes in the database
MATCH (n) RETURN count(n) as total_nodes;

// Create a few sample nodes with different labels
CREATE (p:Person {name: 'Alice Smith', age: 28, role: 'Developer'}) RETURN p;
CREATE (p:Person {name: 'Bob Jones', age: 35, role: 'Manager'}) RETURN p;
CREATE (c:Company {name: 'Tech Corp', founded: 2020}) RETURN c;

// Create relationships between nodes
MATCH (a:Person {name: 'Alice Smith'}), (b:Company {name: 'Tech Corp'})
CREATE (a)-[r:WORKS_FOR {since: 2021}]->(b)
RETURN a, r, b;

// Query the graph structure
MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
RETURN p.name as employee, type(r) as relationship, r.since as start_date, c.name as company;

// Find all people and their properties
MATCH (p:Person)
RETURN p.name, p.age, p.role
ORDER BY p.age DESC; 