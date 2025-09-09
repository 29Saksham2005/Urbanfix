#!/usr/bin/env python3
"""
MongoDB Connection Checker for Urbanfix
This script checks if MongoDB is available and provides setup instructions.
"""

from pymongo import MongoClient
import sys

def check_mongodb():
    """Check if MongoDB is available and provide setup instructions"""
    
    print("🔍 Checking MongoDB connection...")
    
    try:
        # Try to connect to MongoDB Atlas
        MONGODB_URI = 'mongodb+srv://sakshamssingh29_db_user:QTqyzm5c2gRSvosX@complaints.uyqxbrl.mongodb.net/?retryWrites=true&w=majority&appName=complaints'
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        print("✅ MongoDB Atlas is accessible!")
        
        # Check if urbanfix database exists
        db = client['urbanfix']
        collections = db.list_collection_names()
        
        if 'complaints' in collections:
            complaints_count = db['complaints'].count_documents({})
            print(f"📊 Found 'complaints' collection with {complaints_count} documents")
        else:
            print("📝 'complaints' collection not found (will be created automatically)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        print("\n📋 Troubleshooting Steps:")
        print("=" * 50)
        print("1. Check your internet connection")
        print("2. Verify MongoDB Atlas cluster is running")
        print("3. Check if your IP is whitelisted in MongoDB Atlas")
        print("4. Verify the connection string is correct")
        print("5. Check if the database user has proper permissions")
        print()
        print("6. Run migration script:")
        print("   - python migrate_to_mongodb.py")
        print()
        print("7. Start the application:")
        print("   - python python.py")
        print("=" * 50)
        
        return False

if __name__ == "__main__":
    print("🚀 Urbanfix MongoDB Connection Checker")
    print("=" * 40)
    
    if check_mongodb():
        print("\n🎉 Ready to run the application!")
        print("Run: python python.py")
    else:
        print("\n⚠️  Please set up MongoDB first, then run this script again.")
        sys.exit(1)
