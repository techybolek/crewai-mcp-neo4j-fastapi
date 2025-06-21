// First clean up any existing data
MATCH (n)
DETACH DELETE n;

// Create nodes with sample data
// Staff members
MERGE (s1:Staff {name: 'John Smith', role: 'Manager'});
MERGE (s2:Staff {name: 'Sarah Johnson', role: 'Documentation Lead'});
MERGE (s3:Staff {name: 'Mike Brown', role: 'Vendor Relations'});
MERGE (s4:Staff {name: 'Lisa Chen', role: 'Delivery Manager'});

// Companies
MERGE (c1:Company {name: 'Tech Solutions Inc', founded: 2020});
MERGE (c2:Company {name: 'Digital Corp', founded: 2018});

// People (Customers)
MERGE (p1:Person {name: 'Alice Wilson', email: 'alice@email.com'});
MERGE (p2:Person {name: 'Bob Miller', email: 'bob@email.com'});

// Documentation
MERGE (d1:Doc {title: 'Product Manual v1', created_date: '2024-01-15'});
MERGE (d2:Doc {title: 'Technical Specifications', created_date: '2024-02-01'});

// Vendors
MERGE (v1:Vendor {name: 'Supply Masters', rating: 4.5});
MERGE (v2:Vendor {name: 'Quality Goods Ltd', rating: 4.8});

// Products
MERGE (pr1:Product {name: 'Enterprise Software', price: 999.99, sku: 'SW001'});
MERGE (pr2:Product {name: 'Cloud Service', price: 299.99, sku: 'CS002'});

// Orders
MERGE (o1:Order {number: 'ORD001', date: '2024-03-01', status: 'Delivered'});
MERGE (o2:Order {number: 'ORD002', date: '2024-03-05', status: 'In Progress'});

// Delivery Services
MERGE (d1:Delivery {name: 'Express Delivery', type: 'Same Day'});
MERGE (d2:Delivery {name: 'Standard Shipping', type: 'Ground'});

// Create relationships
// Staff working for companies
MATCH (s:Staff {name: 'John Smith'}), (c:Company {name: 'Tech Solutions Inc'})
MERGE (s)-[:WORKS_FOR {since: '2020-01-01'}]->(c);

MATCH (s:Staff {name: 'Sarah Johnson'}), (c:Company {name: 'Tech Solutions Inc'})
MERGE (s)-[:WORKS_FOR {since: '2020-03-15'}]->(c);

// People working for companies
MATCH (p:Person {name: 'Alice Wilson'}), (c:Company {name: 'Digital Corp'})
MERGE (p)-[:WORKS_FOR {since: '2021-01-01'}]->(c);

// Staff writing documentation
MATCH (s:Staff {name: 'Sarah Johnson'}), (d:Doc {title: 'Product Manual v1'})
MERGE (s)-[:WROTE {date: '2024-01-15'}]->(d);

// Staff overseeing vendors
MATCH (s:Staff {name: 'Mike Brown'}), (v:Vendor {name: 'Supply Masters'})
MERGE (s)-[:OVERSEES {since: '2023-06-01'}]->(v);

// Staff managing delivery services
MATCH (s:Staff {name: 'Lisa Chen'}), (d:Delivery {name: 'Express Delivery'})
MERGE (s)-[:MANAGES {since: '2023-01-01'}]->(d);

// Staff assigned to orders
MATCH (s:Staff {name: 'John Smith'}), (o:Order {number: 'ORD001'})
MERGE (s)-[:ASSIGNED_TO {date: '2024-03-01'}]->(o);

// Vendors supplying products
MATCH (v:Vendor {name: 'Supply Masters'}), (p:Product {name: 'Enterprise Software'})
MERGE (v)-[:SUPPLIES {contract_date: '2023-01-01'}]->(p);

// Documentation about products
MATCH (d:Doc {title: 'Product Manual v1'}), (p:Product {name: 'Enterprise Software'})
MERGE (d)-[:ABOUT {version: '1.0'}]->(p);

// Orders containing products
MATCH (o:Order {number: 'ORD001'}), (p:Product {name: 'Enterprise Software'})
MERGE (o)-[:CONTAINS {quantity: 1, price: 999.99}]->(p);

// Orders being delivered
MATCH (o:Order {number: 'ORD001'}), (d:Delivery {name: 'Express Delivery'})
MERGE (o)-[:DELIVERED_BY {scheduled_date: '2024-03-02'}]->(d);

// People making orders
MATCH (p:Person {name: 'Bob Miller'}), (o:Order {number: 'ORD001'})
MERGE (p)-[:MADE {date: '2024-03-01'}]->(o);

// Verify the graph structure
MATCH (n)
RETURN DISTINCT labels(n) as NodeTypes, count(n) as Count;

MATCH ()-[r]->()
RETURN DISTINCT type(r) as RelationType, count(r) as Count; 