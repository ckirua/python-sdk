#!/usr/bin/env python3
"""
Example demonstrating the PGConnectionParameters class from sdk.cnet.parameters.

This example shows how to create and use PGConnectionParameters objects
for building PostgreSQL connection URLs.
"""

from sdk.cnet.parameters import PGConnectionParameters


def main():
    """Demonstrate PGConnectionParameters usage."""
    
    print("=== PGConnectionParameters Example ===\n")
    
    # Example 1: Basic usage
    print("1. Basic usage:")
    pg1 = PGConnectionParameters(
        host="localhost",
        port=5432,
        user="myuser",
        password="mypassword",
        database="mydb"
    )
    print(f"   Connection: {pg1}")
    print(f"   URL: {pg1.url}")
    print()
    
    # Example 2: Different host and port
    print("2. Remote database connection:")
    pg2 = PGConnectionParameters(
        host="db.example.com",
        port=5433,
        user="readonly",
        password="readonly_pass",
        database="analytics"
    )
    print(f"   Connection: {pg2}")
    print(f"   URL: {pg2.url}")
    print()
    
    # Example 3: Show all available fields using properties
    print("3. Object attributes (via properties):")
    print(f"   Host: {pg1.host}")
    print(f"   Port: {pg1.port}")
    print(f"   User: {pg1.user}")
    print(f"   Database: {pg1.database}")
    print(f"   Driver: {pg1.driver}")
    print()
    
    # Example 4: Demonstrate property setters
    print("4. Property setters demonstration:")
    print(f"   Original host: {pg1.host}")
    pg1.host = "newhost.example.com"
    print(f"   New host: {pg1.host}")
    
    print(f"   Original port: {pg1.port}")
    pg1.port = 5433
    print(f"   New port: {pg1.port}")
    
    print(f"   Original user: {pg1.user}")
    pg1.user = "newuser"
    print(f"   New user: {pg1.user}")
    
    print(f"   Original database: {pg1.database}")
    pg1.database = "newdb"
    print(f"   New database: {pg1.database}")
    
    print(f"   Original driver: {pg1.driver}")
    pg1.driver = "postgresql+psycopg2"
    print(f"   New driver: {pg1.driver}")
    
    # Note: password can be set but not viewed for security
    print(f"   Setting new password...")
    pg1.password = "newpassword123"
    print(f"   Password updated (not viewable for security)")
    print()
    
    # Example 5: Show updated URL after changes
    print("5. Updated URL after property changes:")
    print(f"   New URL: {pg1.url}")
    print()
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
