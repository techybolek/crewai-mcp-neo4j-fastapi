import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import argparse

# Load environment variables from .env file
load_dotenv()

def get_env_var(var_name):
    """Get an environment variable or raise an error if it's not set"""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set. Please set it in your .env file.")
    return value

# Get credentials from environment variables
try:
    uri = get_env_var("NEO4J_URI")
    user = get_env_var("NEO4J_USERNAME")
    password = get_env_var("NEO4J_PASSWORD")
except ValueError as e:
    print(f"❌ Configuration error: {str(e)}")
    print("Make sure you have a .env file with NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD")
    exit(1)

class Neo4jOperations:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def test_connection(self):
        try:
            # Verify connectivity
            self.driver.verify_connectivity()
            print("✅ Successfully connected to Neo4j database!")
            
            # Run a simple query to further verify
            with self.driver.session() as session:
                result = session.run("RETURN 1 as num")
                record = result.single()
                print(f"Test query result: {record['num']}")
            return True
            
        except ServiceUnavailable as e:
            print("❌ Failed to connect to Neo4j database!")
            print(f"Error: {str(e)}")
            return False
        except Exception as e:
            print("❌ An error occurred!")
            print(f"Error: {str(e)}")
            return False

    def execute_from_file(self, file_path):
        """
        Execute Neo4j statements from a file.
        Each statement should be separated by a semicolon.
        
        Args:
            file_path (str): Path to the file containing Neo4j statements
            
        Returns:
            list: List of results from each statement execution
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Split content into individual statements
            statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
            
            results = []
            with self.driver.session() as session:
                for i, statement in enumerate(statements, 1):
                    try:
                        print(f"\n📝 Executing statement {i}/{len(statements)}:")
                        print(f"{statement}\n")
                        
                        result = session.run(statement)
                        records = list(result)
                        
                        print(f"✅ Statement {i} executed successfully")
                        if records:
                            print("Results:")
                            for record in records:
                                print(record.data())
                        
                        results.append({
                            'statement': statement,
                            'success': True,
                            'records': [record.data() for record in records]
                        })
                        
                    except Exception as e:
                        print(f"❌ Error executing statement {i}:")
                        print(f"Error: {str(e)}")
                        results.append({
                            'statement': statement,
                            'success': False,
                            'error': str(e)
                        })
            
            return results
            
        except Exception as e:
            print(f"❌ An error occurred while processing the file:")
            print(f"Error: {str(e)}")
            return None

    def create_sample_node(self):
        with self.driver.session() as session:
            # Create a sample Person node
            result = session.run("""
                CREATE (p:Person {
                    name: 'John Doe',
                    age: 30,
                    email: 'john.doe@example.com'
                })
                RETURN p
            """)
            node = result.single()[0]
            print(f"✅ Created new node with properties: {dict(node)}")

    def list_all_nodes(self):
        with self.driver.session() as session:
            # Query to get all nodes with their labels and properties
            result = session.run("""
                MATCH (n)
                RETURN labels(n) as labels, properties(n) as properties
            """)
            
            print("\n📋 All nodes in the database:")
            print("-" * 50)
            for record in result:
                labels = record["labels"]
                props = record["properties"]
                print(f"Labels: {labels}")
                print(f"Properties: {props}")
                print("-" * 50)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Execute Neo4j statements from a file.')
    parser.add_argument('filename', help='Path to the file containing Neo4j statements')
    args = parser.parse_args()

    neo4j_ops = Neo4jOperations()
    
    # Test connection
    if neo4j_ops.test_connection():
        # Execute statements from the specified file
        print(f"\nExecuting statements from file: {args.filename}")
        results = neo4j_ops.execute_from_file(args.filename)
        if results:
            print("\n📊 Summary of execution:")
            print(f"Total statements executed: {len(results)}")
            print(f"Successful: {sum(1 for r in results if r['success'])}")
            print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    neo4j_ops.close() 