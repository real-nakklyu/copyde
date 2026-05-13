from app.core.supabase import SupabaseRestClient


def get_supabase_rest_client() -> SupabaseRestClient:
    return SupabaseRestClient()

