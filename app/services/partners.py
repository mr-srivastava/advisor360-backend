from app.db.supabase import get_supabase

def get_entities():
    supabase = get_supabase()
    data = supabase.table("entities").select("*").execute()
    return data.data

def get_entity_types():
    supabase = get_supabase()
    data = supabase.table("entity_types").select("*").execute()
    return data.data

def get_partners(): 
    entities = get_entities()
    entity_types = get_entity_types()

     # Build a dictionary for quick type lookup
    entity_types_lookup = {etype["id"]: etype["name"] for etype in entity_types}
    
    # Merge entities with their type name
    parnters = []
    for entity in entities:
        parnters.append({
            "id": entity["id"],
            "name": entity["name"],
            "entity_type": entity_types_lookup.get(entity["type_id"]),  # type name
            "created_at": entity["created_at"]
        })

    return parnters
