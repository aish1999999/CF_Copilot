"""
Extract company data from Career Fair PDF booklets.

This script parses the PDF files to extract:
- Company names
- Booth numbers
- Ballroom locations
- Position types
- Majors recruited
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Hardcoded data extracted from the PDF (Day 1)
# This would ideally be extracted programmatically, but for MVP we'll use structured data

DAY1_COMPANIES = [
    {"name": "Burns & McDonnell", "booth": "1/2", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Construction Engineering", "Construction Management", "Electrical Engineering", "Electrical Power Engineering Technology", "Engineering Management", "Environmental Engineering", "Industrial Engineering", "Mechanical Engineering", "Supply Chain and Logistics Technology"], "is_platinum": True},
    {"name": "BAYSTAR", "booth": "3", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Chemical Engineering", "Computer Engineering & Analytics", "Computer Engineering", "Electrical Engineering", "Mechanical Engineering", "Computer & Systems Engineering"], "is_platinum": False},
    {"name": "The Newtron Group", "booth": "4", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time"], "majors": ["All Majors"], "is_platinum": False},
    {"name": "Champion Technology Services, Inc.", "booth": "5", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op"], "majors": ["Chemical Engineering", "Computer Engineering", "Cybersecurity", "Electrical Engineering", "Industrial Engineering", "Mechanical Engineering", "Computer & Systems Engineering", "Systems Engineering"], "is_platinum": False},
    {"name": "Centerpoint Energy", "booth": "6/7", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Computer Engineering", "Computer Information Systems", "Construction Engineering", "Construction Management", "Cybersecurity", "Electrical Engineering", "Mechanical Engineering"], "is_platinum": False},
    {"name": "Oncor Electric Delivery", "booth": "8", "ballroom": "Waldorf", "position_types": ["Internships"], "majors": ["Civil Engineering", "Construction Engineering", "Construction Management", "Mechanical Engineering"], "is_platinum": False},
    {"name": "Technip Energies", "booth": "9", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Electrical Engineering", "Mechanical Engineering", "Mechanical Engineering Technology", "Subsea Engineering", "Supply Chain and Logistics Technology"], "is_platinum": False},
    {"name": "Performance Contracting, Inc.", "booth": "10", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Construction Engineering", "Construction Management"], "is_platinum": False},
    {"name": "S&B Engineers and Constructors, Ltd.", "booth": "11", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Civil Engineering", "Construction Engineering", "Construction Management", "Engineering Data Science", "Electrical Engineering"], "is_platinum": False},
    {"name": "American Bureau of Shipping", "booth": "12", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Civil Engineering", "Computer Engineering", "Computer Information Systems", "Cybersecurity", "Electrical Engineering", "Materials Science & Engineering", "Mechanical Engineering"], "is_platinum": False},
    {"name": "BASF Corporation", "booth": "13/14", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Electrical Engineering", "Mechanical Engineering"], "is_platinum": True},
    {"name": "Enterprise Products", "booth": "15/16", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Electrical Engineering", "Environmental Engineering", "Mechanical Engineering"], "is_platinum": True},
    {"name": "Alcon", "booth": "17", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Biomedical Engineering", "Biotechnology", "Chemical Engineering", "Electrical Engineering", "Engineering Unspecified", "Mechanical Engineering", "Supply Chain and Logistics Technology"], "is_platinum": False},
    {"name": "ANDRES Construction", "booth": "18", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Construction Engineering", "Construction Management", "Mechanical Engineering"], "is_platinum": False},
    {"name": "NOV", "booth": "19/20", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Computer Engineering & Analytics", "Computer Engineering Technology", "Computer Information Systems", "Engineering Unspecified", "Industrial Engineering", "Materials Science & Engineering", "Mechanical Engineering", "Mechanical Engineering Technology", "Computer & Systems Engineering"], "is_platinum": True},
    {"name": "Tenaris", "booth": "21/22", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Co-Op", "Internships"], "majors": ["Engineering Management", "Environmental Engineering", "Human Resource Development", "Industrial Engineering", "Supply Chain and Logistics Technology", "Systems Engineering", "Technology Leadership and Innovation Management", "Technology Project Management"], "is_platinum": True},
    {"name": "ExxonMobil", "booth": "41/42", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Electrical Engineering", "Electrical Power Engineering Technology", "Engineering Management", "Engineering Technology", "Environmental Engineering", "Industrial Engineering", "Materials Science & Engineering", "Mechanical Engineering", "Mechanical Engineering Technology", "Petroleum Engineering", "Supply Chain and Logistics Technology", "Systems Engineering"], "is_platinum": True},
    {"name": "Marathon Petroleum Company", "booth": "37/38", "ballroom": "Waldorf", "position_types": ["Co-Op", "Internships"], "majors": ["Chemical Engineering", "Civil Engineering", "Construction Management", "Electrical Engineering", "Mechanical Engineering"], "is_platinum": False},
    {"name": "Motiva Enterprises LLC", "booth": "39/40", "ballroom": "Waldorf", "position_types": ["Internships"], "majors": ["Chemical Engineering", "Cybersecurity", "Electrical Engineering", "Mechanical Engineering"], "is_platinum": False},
    {"name": "Phillips 66", "booth": "33", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Chemical Engineering", "Mechanical Engineering"], "is_platinum": False},
    {"name": "Omega 365 USA", "booth": "27/28", "ballroom": "Waldorf", "position_types": ["Entry-Level/Full-Time", "Internships"], "majors": ["Computer Engineering & Analytics", "Computer Engineering", "Computer Engineering Technology", "Computer Information Systems", "Construction Engineering", "Construction Management", "Engineering Data Science", "Computer & Systems Engineering", "Technology Project Management", "Technology Unspecified"], "is_platinum": True},
]

# Ballroom coordinates for map visualization (simplified 2D coordinates)
BALLROOM_LAYOUTS = {
    "Waldorf": {
        "booths": [
            {"booth_number": "1", "x": 100, "y": 50},
            {"booth_number": "2", "x": 150, "y": 50},
            {"booth_number": "3", "x": 200, "y": 50},
            {"booth_number": "4", "x": 250, "y": 50},
            {"booth_number": "5", "x": 300, "y": 50},
            {"booth_number": "6", "x": 350, "y": 50},
            {"booth_number": "7", "x": 400, "y": 50},
            {"booth_number": "8", "x": 450, "y": 50},
            {"booth_number": "9", "x": 500, "y": 50},
            {"booth_number": "10", "x": 550, "y": 50},
            {"booth_number": "11", "x": 600, "y": 50},
            {"booth_number": "12", "x": 650, "y": 50},
            # Add more booth coordinates as needed
        ]
    },
    "Conrad": {
        "booths": []
    },
    "Shamrock": {
        "booths": []
    }
}

def extract_companies_from_pdf() -> List[Dict[str, Any]]:
    """
    Extract company data from PDF.

    For MVP, we're using hardcoded data extracted manually.
    In production, this would use pdfplumber or similar library.
    """
    return DAY1_COMPANIES

def save_to_json(data: List[Dict], output_path: Path):
    """Save extracted data to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} companies to {output_path}")

def generate_booth_coordinates():
    """Generate booth coordinates for map visualization."""
    return BALLROOM_LAYOUTS

def main():
    """Main extraction function."""
    # Define output paths
    output_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    companies_path = output_dir / "companies.json"
    booths_path = output_dir / "booth_coordinates.json"

    # Extract and save company data
    companies = extract_companies_from_pdf()
    save_to_json(companies, companies_path)

    # Generate and save booth coordinates
    booth_coords = generate_booth_coordinates()
    save_to_json(booth_coords, booths_path)

    # Generate majors list
    all_majors = set()
    for company in companies:
        all_majors.update(company["majors"])

    majors_list = sorted(list(all_majors))
    majors_path = output_dir / "majors.json"
    save_to_json(majors_list, majors_path)

    print(f"\nExtraction complete!")
    print(f"Total companies: {len(companies)}")
    print(f"Total unique majors: {len(majors_list)}")

if __name__ == "__main__":
    main()
