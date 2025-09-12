#!/usr/bin/env python3
"""
Material Duplication Example Script

This script demonstrates how to use the MaterialDuplicationManager
to duplicate course materials across multiple sections.

Use Case 1: Duplicate same materials to multiple sections
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path.resolve()))

from moodle_client import MoodleAPIClient
from material_duplicator import MaterialDuplicationManager, DuplicationJob, MaterialType


def example_duplicate_assignments_and_quizzes():
    """
    Example: Duplicate all assignments and quizzes from one course to multiple sections
    """
    print("=" * 60)
    print("EXAMPLE 1: Duplicate Assignments & Quizzes")
    print("=" * 60)
    
    # Initialize client (configure with real credentials)
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    manager = MaterialDuplicationManager(client)
    
    # Configure duplication job
    job = DuplicationJob(
        source_course_id=99,  # Source course (e.g., UCLC1009 Section 1)
        target_course_ids=[100, 101, 102],  # Target courses (other sections)
        material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ},
        include_hidden=False,
        preserve_dates=True
    )
    
    print(f"Source Course: {job.source_course_id}")
    print(f"Target Courses: {job.target_course_ids}")
    print(f"Material Types: {[mt.value for mt in job.material_types]}")
    print()
    
    try:
        # Execute duplication
        print("Starting duplication process...")
        results = manager.duplicate_materials_bulk(job)
        
        # Generate report
        report = manager.generate_duplication_report(results)
        
        # Display results
        print("Duplication completed!")
        print(f"Total operations: {report['summary']['total_operations']}")
        print(f"Successful: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success rate: {report['summary']['success_rate']:.1f}%")
        
        # Show details by course
        print("\nResults by Target Course:")
        for course_id, stats in report['by_course'].items():
            print(f"  Course {course_id}: {stats['success']} successful, {stats['failed']} failed")
        
        # Show failed operations if any
        if report['failed_operations']:
            print("\nFailed Operations:")
            for failed in report['failed_operations']:
                print(f"  - {failed['material_name']} -> Course {failed['target_course']}: {failed['error']}")
    
    except Exception as e:
        print(f"Duplication failed: {e}")


def example_duplicate_all_materials():
    """
    Example: Duplicate ALL course materials to new sections
    """
    print("=" * 60)
    print("EXAMPLE 2: Duplicate All Materials")
    print("=" * 60)
    
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    manager = MaterialDuplicationManager(client)
    
    # Configure to duplicate everything
    job = DuplicationJob(
        source_course_id=99,
        target_course_ids=[200, 201],  # New course sections
        material_types={MaterialType.ALL},  # All material types
        include_hidden=True,  # Include hidden materials
        preserve_dates=True
    )
    
    print(f"Duplicating ALL materials from course {job.source_course_id}")
    print(f"To courses: {job.target_course_ids}")
    print("Including hidden materials: YES")
    print()
    
    try:
        results = manager.duplicate_materials_bulk(job)
        report = manager.generate_duplication_report(results)
        
        print("Results:")
        print(f"Total materials duplicated: {report['summary']['successful']}")
        print(f"Failed duplications: {report['summary']['failed']}")
        
        # Show breakdown by material type
        print("\nBy Material Type:")
        for mat_type, stats in report['by_material_type'].items():
            total_type = stats['success'] + stats['failed']
            print(f"  {mat_type}: {stats['success']}/{total_type} successful")
    
    except Exception as e:
        print(f"Duplication failed: {e}")


def example_duplicate_with_section_mapping():
    """
    Example: Duplicate materials with custom section mapping
    """
    print("=" * 60)
    print("EXAMPLE 3: Duplicate with Section Mapping")
    print("=" * 60)
    
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    manager = MaterialDuplicationManager(client)
    
    # Configure with section mapping
    job = DuplicationJob(
        source_course_id=99,
        target_course_ids=[300],
        material_types={MaterialType.ASSIGNMENT, MaterialType.RESOURCE},
        section_mapping={
            0: 1,  # General section -> Week 1
            1: 2,  # Week 1 -> Week 2
            2: 3,  # Week 2 -> Week 3
        },
        include_hidden=False
    )
    
    print("Section Mapping:")
    for source_sec, target_sec in job.section_mapping.items():
        print(f"  Source Section {source_sec} -> Target Section {target_sec}")
    print()
    
    try:
        results = manager.duplicate_materials_bulk(job)
        report = manager.generate_duplication_report(results)
        
        print(f"Materials duplicated: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
    
    except Exception as e:
        print(f"Duplication failed: {e}")


def example_preview_materials():
    """
    Example: Preview what materials would be duplicated (without actually duplicating)
    """
    print("=" * 60)
    print("EXAMPLE 4: Preview Materials")
    print("=" * 60)
    
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    manager = MaterialDuplicationManager(client)
    
    try:
        # Get materials that would be duplicated
        materials = manager.get_course_materials(
            course_id=99,
            material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ, MaterialType.FORUM},
            include_hidden=False
        )
        
        print(f"Found {len(materials)} materials to duplicate:")
        print("-" * 40)
        
        for material in materials:
            print(f"• {material.get('name', 'Unnamed')} ({material.get('modname', 'unknown')})")
            print(f"  Section: {material.get('source_section_name', 'Unknown')}")
            print(f"  Visible: {'Yes' if material.get('visible', True) else 'No'}")
            print()
    
    except Exception as e:
        print(f"Preview failed: {e}")


def main():
    """Main function to run examples"""
    print("MATERIAL DUPLICATION EXAMPLES")
    print("=" * 60)
    print()
    print("This script demonstrates how to duplicate course materials")
    print("across multiple sections using the new Moodle API functions.")
    print()
    print("IMPORTANT: Configure real Moodle credentials before running!")
    print()
    
    # Run examples (commented out to avoid accidental execution)
    print("Available examples:")
    print("1. Duplicate assignments and quizzes")
    print("2. Duplicate all materials")
    print("3. Duplicate with section mapping")
    print("4. Preview materials")
    print()
    print("Uncomment the desired example in the main() function to run it.")
    
    # Uncomment to run examples:
    # example_preview_materials()
    # example_duplicate_assignments_and_quizzes()
    # example_duplicate_all_materials()
    # example_duplicate_with_section_mapping()


if __name__ == "__main__":
    main()
