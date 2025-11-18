"""
Seed database with career fair data from extracted JSON files.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models.company import Company, PositionType, MajorRecruited
from app.models.booth import Booth


def load_json_data(filepath: Path):
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def seed_companies(db, companies_data):
    """Seed companies and related data."""
    print(f"Seeding {len(companies_data)} companies...")

    for company_data in companies_data:
        # Create company
        company = Company(
            name=company_data["name"],
            booth_number=company_data["booth"],
            ballroom=company_data["ballroom"],
            is_platinum_sponsor=company_data.get("is_platinum", False),
        )
        db.add(company)
        db.flush()  # Get company ID

        # Add position types
        for position_type in company_data.get("position_types", []):
            pt = PositionType(
                company_id=company.id,
                position_type=position_type,
            )
            db.add(pt)

        # Add majors recruited
        for major in company_data.get("majors", []):
            mr = MajorRecruited(
                company_id=company.id,
                major_name=major,
            )
            db.add(mr)

        # Create booth entry
        # Parse booth number for coordinates (simplified)
        booth_num = company_data["booth"].split("/")[0]  # Handle ranges like "1/2"

        # Check if booth already exists
        existing_booth = db.query(Booth).filter(Booth.booth_number == company_data["booth"]).first()

        if not existing_booth:
            # Simple coordinate assignment based on booth number (can be improved)
            try:
                booth_int = int(booth_num)
                x = (booth_int % 10) * 100
                y = (booth_int // 10) * 100
            except:
                x, y = 0, 0

            booth = Booth(
                booth_number=company_data["booth"],
                ballroom=company_data["ballroom"],
                coordinate_x=x,
                coordinate_y=y,
                queue_length=0,
                service_time_estimate=5.0,
            )
            db.add(booth)

    db.commit()
    print(f"✓ Seeded {len(companies_data)} companies successfully!")


def main():
    """Main seeding function."""
    # Initialize database
    print("Initializing database...")
    init_db()

    # Get data directory
    data_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    companies_file = data_dir / "companies.json"

    if not companies_file.exists():
        print(f"Error: {companies_file} not found!")
        print("Please run extract_pdf_data.py first.")
        return

    # Load data
    companies_data = load_json_data(companies_file)

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(MajorRecruited).delete()
        db.query(PositionType).delete()
        db.query(Booth).delete()
        db.query(Company).delete()
        db.commit()
        print("✓ Cleared existing data")

        # Seed companies
        seed_companies(db, companies_data)

        print("\n✅ Database seeded successfully!")
        print(f"Total companies: {db.query(Company).count()}")
        print(f"Total booths: {db.query(Booth).count()}")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
