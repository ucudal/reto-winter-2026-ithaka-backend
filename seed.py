import sys
from app.core.db.seed import seed_database

if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed_database(force=force_flag)
