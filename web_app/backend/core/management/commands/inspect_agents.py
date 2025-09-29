from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings
from core.models import Files

class Command(BaseCommand):
    help = 'Inspect agent inputs and outputs without running them'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, default=1, help='User ID to inspect')

    def handle(self, *args, **options):
        user_id = options['user_id']
        
        self.stdout.write("🔍 Inspecting Agent Setup")
        self.stdout.write("=" * 50)
        
        # Check uploaded databases
        files = Files.objects.filter(user_id=user_id)
        self.stdout.write(f"\n📁 Uploaded Databases ({files.count()} total):")
        for file in files[:10]:  # Show first 10
            self.stdout.write(f"  - {file.database}")
        if files.count() > 10:
            self.stdout.write(f"  ... and {files.count() - 10} more")
        
        # Check schema files
        schema_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), "schema")
        schema_ab_file = os.path.join(schema_dir, "schema_ab.jsonl")
        schema_c_file = os.path.join(schema_dir, "schema_c.json")
        
        self.stdout.write(f"\n📋 Schema Files:")
        self.stdout.write(f"  Schema AB: {'✅' if os.path.exists(schema_ab_file) else '❌'}")
        self.stdout.write(f"  Schema C: {'✅' if os.path.exists(schema_c_file) else '❌'}")
        
        # Show sample schema data
        if os.path.exists(schema_ab_file):
            self.stdout.write(f"\n📊 Schema AB Sample (first 3 entries):")
            with open(schema_ab_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 3:
                        break
                    if line.strip():
                        try:
                            obj = json.loads(line.strip())
                            self.stdout.write(f"  {i+1}. DB: {obj.get('database', 'N/A')}, Table: {obj.get('table', 'N/A')}")
                            self.stdout.write(f"     Columns: {', '.join(obj.get('columns', [])[:5])}{'...' if len(obj.get('columns', [])) > 5 else ''}")
                        except:
                            self.stdout.write(f"  {i+1}. Invalid JSON: {line.strip()[:50]}...")
        
        # Show sample schema C data
        if os.path.exists(schema_c_file):
            self.stdout.write(f"\n📊 Schema C Sample:")
            with open(schema_c_file, 'r') as f:
                try:
                    schema_c = json.load(f)
                    db_names = list(schema_c.keys())[:3]
                    for db_name in db_names:
                        self.stdout.write(f"  Database: {db_name}")
                        tables = schema_c[db_name].get('tables', {})
                        table_names = list(tables.keys())[:2]
                        for table_name in table_names:
                            self.stdout.write(f"    Table: {table_name}")
                            columns = tables[table_name].get('columns', [])
                            self.stdout.write(f"      Columns: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}")
                except Exception as e:
                    self.stdout.write(f"  ❌ Error reading schema C: {e}")
        
        # Show what Agent A would receive
        self.stdout.write(f"\n🤖 Agent A Input/Output Flow:")
        self.stdout.write(f"  Input: {{'query': 'Show me all students'}}")
        self.stdout.write(f"  Process: Uses embeddings to find relevant database")
        self.stdout.write(f"  Output: {{'query': '...', 'database': 'college_1', 'reasons': '...'}}")
        
        # Show what Agent B would receive
        self.stdout.write(f"\n🤖 Agent B Input/Output Flow:")
        self.stdout.write(f"  Input: Agent A output + schema_ab.jsonl")
        self.stdout.write(f"  Process: Analyzes database schema to select relevant tables")
        self.stdout.write(f"  Output: {{'query': '...', 'database': 'college_1', 'tables': ['students'], 'reasons': '...'}}")
        
        # Show what Agent C would receive
        self.stdout.write(f"\n🤖 Agent C Input/Output Flow:")
        self.stdout.write(f"  Input: Agent B output + schema_c.json")
        self.stdout.write(f"  Process: Generates SQL query using table schemas")
        self.stdout.write(f"  Output: {{'query': '...', 'database': 'college_1', 'tables': ['students'], 'SQL': 'SELECT * FROM students', 'reasons': '...'}}")
        
        self.stdout.write(f"\n💡 To test with real API key:")
        self.stdout.write(f"  python manage.py test_agents --api-key YOUR_OPENAI_KEY --query 'Show me all students'")
