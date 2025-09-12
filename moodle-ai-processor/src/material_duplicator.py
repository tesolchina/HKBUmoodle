"""
Material Duplication Manager

This module provides functionality to duplicate course materials 
(assignments, quizzes, forums, resources, etc.) from one course section 
to multiple target sections.

Use Case 1: Duplicate same materials to multiple sections
"""

import json
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

# Assuming moodle_client is available
from moodle_client import MoodleAPIClient


class MaterialType(Enum):
    """Types of course materials that can be duplicated"""
    ASSIGNMENT = "assign"
    QUIZ = "quiz"
    FORUM = "forum"
    RESOURCE = "resource"
    URL = "url"
    PAGE = "page"
    BOOK = "book"
    FOLDER = "folder"
    LABEL = "label"
    ALL = "all"


@dataclass
class DuplicationResult:
    """Result of a material duplication operation"""
    source_module_id: int
    target_course_id: int
    target_module_id: Optional[int]
    success: bool
    error_message: Optional[str] = None
    material_type: Optional[str] = None
    material_name: Optional[str] = None


@dataclass
class DuplicationJob:
    """Configuration for a duplication job"""
    source_course_id: int
    target_course_ids: List[int]
    material_types: Set[MaterialType]
    section_mapping: Optional[Dict[int, int]] = None  # source_section -> target_section
    include_hidden: bool = False
    preserve_dates: bool = True


class MaterialDuplicationManager:
    """Manager for duplicating course materials across sections"""
    
    def __init__(self, moodle_client: MoodleAPIClient):
        """
        Initialize the duplication manager
        
        Args:
            moodle_client: Authenticated Moodle API client
        """
        self.client = moodle_client
        self.logger = logging.getLogger(__name__)
    
    def get_course_materials(self, course_id: int, 
                           material_types: Set[MaterialType] = None,
                           include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        Get all materials from a course that match the specified types
        
        Args:
            course_id: Source course ID
            material_types: Set of material types to include (None for all)
            include_hidden: Whether to include hidden materials
            
        Returns:
            List of course materials (modules/activities)
        """
        try:
            # Get course contents
            course_contents = self.client.get_course_contents(course_id)
            materials = []
            
            for section in course_contents:
                if 'modules' not in section:
                    continue
                    
                for module in section['modules']:
                    # Skip hidden materials if not requested
                    if not include_hidden and not module.get('visible', True):
                        continue
                    
                    # Filter by material type if specified
                    if material_types and MaterialType.ALL not in material_types:
                        module_type = module.get('modname', '')
                        if not any(mt.value == module_type for mt in material_types):
                            continue
                    
                    # Add section info to module
                    module['source_section'] = section.get('section', 0)
                    module['source_section_name'] = section.get('name', '')
                    materials.append(module)
            
            return materials
            
        except Exception as e:
            self.logger.error(f"Failed to get course materials: {e}")
            raise
    
    def duplicate_material_to_course(self, source_material: Dict[str, Any], 
                                   target_course_id: int,
                                   target_section: int = 0) -> DuplicationResult:
        """
        Duplicate a single material to a target course
        
        Args:
            source_material: Source material/module data
            target_course_id: Target course ID
            target_section: Target section number (0 for first section)
            
        Returns:
            DuplicationResult with operation status
        """
        try:
            material_type = source_material.get('modname', 'unknown')
            material_name = source_material.get('name', 'Unnamed')
            source_id = source_material.get('id', 0)
            
            self.logger.info(f"Duplicating {material_type}: {material_name} to course {target_course_id}")
            
            # Prepare module data for creation
            module_data = self._prepare_module_data(source_material, target_section)
            
            # Create the module in target course
            result = self.client.add_module(target_course_id, module_data)
            
            if result and 'cmid' in result:
                return DuplicationResult(
                    source_module_id=source_id,
                    target_course_id=target_course_id,
                    target_module_id=result['cmid'],
                    success=True,
                    material_type=material_type,
                    material_name=material_name
                )
            else:
                return DuplicationResult(
                    source_module_id=source_id,
                    target_course_id=target_course_id,
                    target_module_id=None,
                    success=False,
                    error_message="Failed to create module - no cmid returned",
                    material_type=material_type,
                    material_name=material_name
                )
                
        except Exception as e:
            return DuplicationResult(
                source_module_id=source_material.get('id', 0),
                target_course_id=target_course_id,
                target_module_id=None,
                success=False,
                error_message=str(e),
                material_type=source_material.get('modname', 'unknown'),
                material_name=source_material.get('name', 'Unnamed')
            )
    
    def _prepare_module_data(self, source_material: Dict[str, Any], 
                           target_section: int) -> Dict[str, Any]:
        """
        Prepare module data for creation in target course
        
        Args:
            source_material: Source material/module data
            target_section: Target section number
            
        Returns:
            Module data dictionary for API call
        """
        # Base module data
        module_data = {
            'modulename': source_material.get('modname', ''),
            'section': target_section,
            'name': source_material.get('name', ''),
            'visible': source_material.get('visible', 1)
        }
        
        # Add specific data based on module type
        modname = source_material.get('modname', '')
        
        if modname == 'assign':
            module_data.update(self._prepare_assignment_data(source_material))
        elif modname == 'quiz':
            module_data.update(self._prepare_quiz_data(source_material))
        elif modname == 'forum':
            module_data.update(self._prepare_forum_data(source_material))
        elif modname == 'resource':
            module_data.update(self._prepare_resource_data(source_material))
        elif modname == 'url':
            module_data.update(self._prepare_url_data(source_material))
        elif modname == 'page':
            module_data.update(self._prepare_page_data(source_material))
        
        return module_data
    
    def _prepare_assignment_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare assignment-specific data"""
        return {
            'introformat': 1,
            'intro': 'Duplicated assignment',
            'assignsubmission_onlinetext_enabled': 1,
            'assignsubmission_file_enabled': 1
        }
    
    def _prepare_quiz_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare quiz-specific data"""
        return {
            'introformat': 1,
            'intro': 'Duplicated quiz',
            'timeopen': 0,
            'timeclose': 0,
            'attempts': 0,
            'grade': 100
        }
    
    def _prepare_forum_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare forum-specific data"""
        return {
            'introformat': 1,
            'intro': 'Duplicated forum',
            'type': 'general'
        }
    
    def _prepare_resource_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare resource-specific data"""
        return {
            'introformat': 1,
            'intro': 'Duplicated resource'
        }
    
    def _prepare_url_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare URL-specific data"""
        return {
            'introformat': 1,
            'intro': 'Duplicated URL',
            'externalurl': 'https://example.com'  # Would need to extract from source
        }
    
    def _prepare_page_data(self, source_material: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare page-specific data"""
        return {
            'introformat': 1,
            'content': 'Duplicated page content',
            'contentformat': 1
        }
    
    def duplicate_materials_bulk(self, job: DuplicationJob) -> List[DuplicationResult]:
        """
        Duplicate materials from source course to multiple target courses
        
        Args:
            job: DuplicationJob configuration
            
        Returns:
            List of DuplicationResult objects
        """
        results = []
        
        try:
            # Get materials from source course
            source_materials = self.get_course_materials(
                job.source_course_id,
                job.material_types,
                job.include_hidden
            )
            
            self.logger.info(f"Found {len(source_materials)} materials to duplicate")
            
            # Duplicate to each target course
            for target_course_id in job.target_course_ids:
                self.logger.info(f"Duplicating to course {target_course_id}")
                
                for material in source_materials:
                    # Determine target section
                    source_section = material.get('source_section', 0)
                    if job.section_mapping and source_section in job.section_mapping:
                        target_section = job.section_mapping[source_section]
                    else:
                        target_section = source_section  # Same section number
                    
                    # Duplicate the material
                    result = self.duplicate_material_to_course(
                        material, target_course_id, target_section
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk duplication failed: {e}")
            raise
    
    def generate_duplication_report(self, results: List[DuplicationResult]) -> Dict[str, Any]:
        """
        Generate a summary report of duplication results
        
        Args:
            results: List of DuplicationResult objects
            
        Returns:
            Report dictionary with statistics and details
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        # Group by target course
        by_course = {}
        for result in results:
            course_id = result.target_course_id
            if course_id not in by_course:
                by_course[course_id] = {'success': 0, 'failed': 0, 'materials': []}
            
            if result.success:
                by_course[course_id]['success'] += 1
            else:
                by_course[course_id]['failed'] += 1
            
            by_course[course_id]['materials'].append({
                'name': result.material_name,
                'type': result.material_type,
                'success': result.success,
                'error': result.error_message
            })
        
        # Group by material type
        by_type = {}
        for result in results:
            mat_type = result.material_type or 'unknown'
            if mat_type not in by_type:
                by_type[mat_type] = {'success': 0, 'failed': 0}
            
            if result.success:
                by_type[mat_type]['success'] += 1
            else:
                by_type[mat_type]['failed'] += 1
        
        return {
            'summary': {
                'total_operations': total,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total * 100) if total > 0 else 0
            },
            'by_course': by_course,
            'by_material_type': by_type,
            'failed_operations': [
                {
                    'material_name': r.material_name,
                    'material_type': r.material_type,
                    'target_course': r.target_course_id,
                    'error': r.error_message
                }
                for r in results if not r.success
            ]
        }


def main():
    """Example usage of MaterialDuplicationManager"""
    
    # This would be configured with real Moodle credentials
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    manager = MaterialDuplicationManager(client)
    
    # Example: Duplicate all assignments and quizzes from course 99 to courses 100, 101, 102
    job = DuplicationJob(
        source_course_id=99,
        target_course_ids=[100, 101, 102],
        material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ},
        include_hidden=False,
        preserve_dates=True
    )
    
    print("Starting material duplication...")
    results = manager.duplicate_materials_bulk(job)
    
    # Generate and display report
    report = manager.generate_duplication_report(results)
    
    print("Duplication Report:")
    print("=" * 50)
    print(f"Total operations: {report['summary']['total_operations']}")
    print(f"Successful: {report['summary']['successful']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    
    if report['failed_operations']:
        print("\nFailed Operations:")
        for failed in report['failed_operations']:
            print(f"  - {failed['material_name']} ({failed['material_type']}) -> Course {failed['target_course']}: {failed['error']}")


if __name__ == "__main__":
    main()
