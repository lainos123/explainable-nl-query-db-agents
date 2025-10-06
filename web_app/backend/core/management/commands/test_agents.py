from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings
from core.models import Files
from agents import a_db_select, b_table_select, c_sql_generate


class Command(BaseCommand):
    help = "Test the agent pipeline"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id", type=int, default=1, help="User ID to test with"
        )
        parser.add_argument("--query", type=str, help="Query to test")
        parser.add_argument(
            "--agent",
            type=str,
            choices=["a", "b", "c", "all"],
            default="all",
            help="Which agent to test",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        query = options["query"] or "Show me all students in the database"
        agent = options["agent"]

        # Get API key from user's account
        from core.models import APIKeys

        try:
            api_key_obj = APIKeys.objects.get(user_id=user_id)
            api_key = api_key_obj.api_key
            if not api_key:
                self.stdout.write(
                    self.style.ERROR(
                        f"User {user_id} has no API key set. Please set it in the web interface."
                    )
                )
                return
        except APIKeys.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"User {user_id} has no API key set. Please set it in the web interface."
                )
            )
            return

        self.stdout.write("🧪 Testing Agents")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Query: {query}")
        self.stdout.write(f"User ID: {user_id}")
        self.stdout.write(f"Agent: {agent}")
        self.stdout.write("=" * 50)

        # Check setup first
        self.check_setup(user_id)

        if agent in ["a", "all"]:
            self.test_agent_a(api_key, user_id, query)

        if agent in ["b", "all"]:
            self.test_agent_b(api_key, user_id, query)

        if agent in ["c", "all"]:
            self.test_agent_c(api_key, user_id, query)

    def check_setup(self, user_id):
        """Check if system is properly set up"""
        self.stdout.write("\n🔍 Checking Setup:")

        # Check uploaded databases
        files = Files.objects.filter(user_id=user_id)
        if files.exists():
            self.stdout.write(f"✅ Found {files.count()} uploaded databases")
            for file in files[:3]:  # Show first 3
                self.stdout.write(f"  - {file.database}")
        else:
            self.stdout.write(self.style.ERROR("❌ No databases uploaded"))
            return False

        # Check schema files
        schema_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), "schema")
        schema_ab_file = os.path.join(schema_dir, "schema_ab.jsonl")
        schema_c_file = os.path.join(schema_dir, "schema_c.json")

        self.stdout.write(f"📋 Schema Files:")
        self.stdout.write(
            f"  Schema AB: {'✅' if os.path.exists(schema_ab_file) else '❌'}"
        )
        self.stdout.write(
            f"  Schema C: {'✅' if os.path.exists(schema_c_file) else '❌'}"
        )

        return True

    def test_agent_a(self, api_key, user_id, query):
        """Test Agent A"""
        self.stdout.write("\n🔍 Testing Agent A - Database Selection:")
        self.stdout.write("-" * 40)

        payload = {"query": query}
        try:
            result = a_db_select.run(api_key, payload, user_id)
            self.stdout.write(json.dumps(result, indent=2))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Agent A failed: {e}"))
            return None

    def test_agent_b(self, api_key, user_id, query):
        """Test Agent B"""
        self.stdout.write("\n📋 Testing Agent B - Table Selection:")
        self.stdout.write("-" * 40)

        # First run Agent A to get database
        agent_a_result = self.test_agent_a(api_key, user_id, query)
        if not agent_a_result or "database" not in agent_a_result:
            self.stdout.write(self.style.ERROR("❌ Agent A result missing database"))
            return None

        try:
            result = b_table_select.run(api_key, agent_a_result, user_id)
            self.stdout.write(json.dumps(result, indent=2))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Agent B failed: {e}"))
            return None

    def test_agent_c(self, api_key, user_id, query):
        """Test Agent C"""
        self.stdout.write("\n⚡ Testing Agent C - SQL Generation:")
        self.stdout.write("-" * 40)

        # First run Agent B to get tables
        agent_b_result = self.test_agent_b(api_key, user_id, query)
        if not agent_b_result or "relevant_tables" not in agent_b_result:
            self.stdout.write(
                self.style.ERROR("❌ Agent B result missing relevant_tables")
            )
            return None

        try:
            result = c_sql_generate.run(api_key, agent_b_result, user_id)
            self.stdout.write(json.dumps(result, indent=2))

            if "SQL" in result:
                self.stdout.write("\n🎯 Generated SQL:")
                self.stdout.write("-" * 30)
                self.stdout.write(result["SQL"])
                self.stdout.write("-" * 30)

            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Agent C failed: {e}"))
            return None
