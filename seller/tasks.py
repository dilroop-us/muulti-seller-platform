import redis
from celery import shared_task
from django.db import connection
from django.utils import timezone
from django.db import transaction
from .models import SellerStore

# Configure Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)


@shared_task
def sync_verified_ids_to_redis():
    """
    Syncs the 'ID' column from PostgreSQL's 'verified_sellers' table to Redis.
    """
    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT tax_id FROM verified_sellers")
            ids = [str(row[0]) for row in cursor.fetchall()]  # Extract IDs as strings

        # Clear existing Redis data for verified IDs
        redis_client.delete("verified_ids")

        # Sync IDs to Redis using batch operation
        if ids:
            redis_client.sadd("verified_ids", *ids)

        return {"status": "success", "count": len(ids)}

    except Exception as e:
        return {"status": "error", "message": str(e)}




@shared_task
def validate_id(submitted_id):
    """
    Validates if the submitted tax ID exists in Redis and updates store verification status.
    """
    submitted_id_str = str(submitted_id)  # Ensure ID is a string for Redis comparison

    if redis_client.sismember("verified_ids", submitted_id_str):
        try:
            with transaction.atomic():
                store = SellerStore.objects.get(tax_id=submitted_id)
                store.is_verified = True
                store.verified_at = timezone.now()
                store.save()
                return {"status": "success", "message": f"Store {store.store_name} verified."}
        except SellerStore.DoesNotExist:
            return {"status": "failed", "message": "ID is verified but no matching store found."}
    else:
        return {"status": "failed", "message": "ID is not verified."}

