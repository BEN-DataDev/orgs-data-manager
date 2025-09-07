from supabase import create_client, Client
from dotenv import dotenv_values

# Load values directly from the .env file
config = dotenv_values()

url: str = str(config.get("PUBLIC_SUPABASE_URL"))
key: str = str(config.get("PUBLIC_SUPABASE_ANON_KEY"))
supabase: Client = create_client(url, key)
response = (
    supabase.schema('community_orgs')
    .table("roles")
    .select("*")
    .execute()
)
print(response)  # Print the response data for debugging
print(response.data)  # Print the response data for debugging