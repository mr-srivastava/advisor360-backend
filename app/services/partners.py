from app.db.supabase import get_supabase
from app.core.exceptions import PartnerNotFound, DatabaseError

def get_entities():
    """Get all entities from the database"""
    try:
        supabase = get_supabase()
        data = supabase.table("entities").select("*").execute()
        return data.data or []
    except Exception as e:
        raise DatabaseError(f"Failed to fetch entities: {str(e)}")

def get_entity_types():
    """Get all entity types from the database"""
    try:
        supabase = get_supabase()
        data = supabase.table("entity_types").select("*").execute()
        return data.data or []
    except Exception as e:
        raise DatabaseError(f"Failed to fetch entity types: {str(e)}")

def get_partners(): 
    """Get all partners with their entity types"""
    try:
        entities = get_entities()
        entity_types = get_entity_types()

        # Build a dictionary for quick type lookup
        entity_types_lookup = {etype["id"]: etype["name"] for etype in entity_types}
        
        # Merge entities with their type name
        partners = []
        for entity in entities:
            partners.append({
                "id": entity["id"],
                "name": entity["name"],
                "entity_type": entity_types_lookup.get(entity["type_id"]),  # type name
                "created_at": entity["created_at"]
            })

        return partners
    except Exception as e:
        raise DatabaseError(f"Failed to fetch partners: {str(e)}")

def get_partner_by_id(partner_id: str):
    """Get a specific partner by ID"""
    try:
        partners = get_partners()
        partner = next((p for p in partners if p["id"] == partner_id), None)
        
        if not partner:
            raise PartnerNotFound(partner_id)
        
        return partner
    except PartnerNotFound:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to fetch partner: {str(e)}")
