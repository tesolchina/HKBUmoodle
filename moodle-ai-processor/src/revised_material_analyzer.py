"""
Revised Material Duplication Strategy

Given the API limitations discovered, this module provides
alternative approaches for material duplication that work
with the available APIs.

API Limitations:
- core_course_add_module: NOT AVAILABLE
- core_course_create_sections: NOT AVAILABLE  
- mod_quiz_get_quiz_by_instance: NOT AVAILABLE
- core_course_update_module: May be core_course_edit_module

Alternative Strategies:
1. Focus on content analysis and reporting
2. Use backup/restore approaches
3. Template-based duplication
4. Manual creation + programmatic updates
"""

import json
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from moodle_client import MoodleAPIClient


class MaterialType(Enum):
    """Types of course materials that can be analyzed"""
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
class MaterialAnalysis:
    """Analysis result for a course material"""
    module_id: int
    name: str
    module_type: str
    section_number: int
    section_name: str
    visible: bool
    course_id: int
    can_duplicate: bool
    duplication_method: str
    notes: Optional[str] = None


@dataclass
class DuplicationPlan:
    """Plan for material duplication with available APIs"""
    source_course_id: int
    target_course_ids: List[int]
    materials: List[MaterialAnalysis]
    strategy: str
    manual_steps: List[str]
    automated_steps: List[str]


class RevisedMaterialAnalyzer:
    """
    Analyzes course materials and provides duplication strategies
    that work with available APIs
    """
    
    def __init__(self, moodle_client: MoodleAPIClient):
        self.client = moodle_client
        self.logger = logging.getLogger(__name__)
    
    def analyze_course_materials(self, course_id: int) -> List[MaterialAnalysis]:
        """
        Analyze all materials in a course and determine duplication possibilities
        """
        try:
            contents = self.client.get_course_contents(course_id)
            analyses = []
            
            for section in contents:
                section_num = section.get('section', 0)
                section_name = section.get('name', f'Section {section_num}')
                
                if 'modules' not in section:
                    continue
                
                for module in section['modules']:
                    analysis = self._analyze_module(module, section_num, section_name, course_id)
                    analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to analyze course materials: {e}")
            raise
    
    def _analyze_module(self, module: Dict[str, Any], section_num: int, 
                       section_name: str, course_id: int) -> MaterialAnalysis:
        """Analyze a single module for duplication possibilities"""
        
        module_type = module.get('modname', 'unknown')
        module_id = module.get('id', 0)
        name = module.get('name', 'Unnamed')
        visible = module.get('visible', True)
        
        # Determine duplication strategy based on module type and API availability
        can_duplicate, method, notes = self._get_duplication_strategy(module_type, module)
        
        return MaterialAnalysis(
            module_id=module_id,
            name=name,
            module_type=module_type,
            section_number=section_num,
            section_name=section_name,
            visible=visible,
            course_id=course_id,
            can_duplicate=can_duplicate,
            duplication_method=method,
            notes=notes
        )
    
    def _get_duplication_strategy(self, module_type: str, module: Dict[str, Any]) -> tuple:
        """
        Determine the best duplication strategy for a module type
        given API limitations
        """
        
        strategies = {
            'assign': (False, 'manual_template', 'Create assignment template, duplicate course'),
            'quiz': (False, 'manual_template', 'Create quiz template, use backup/restore'),
            'forum': (True, 'forum_api', 'Use mod_forum_add_discussion API'),
            'resource': (False, 'manual_upload', 'Upload files manually, update via API'),
            'url': (False, 'manual_create', 'Create URL manually, update link via API'),
            'page': (False, 'manual_template', 'Create page template, update content via API'),
            'book': (False, 'manual_template', 'Create book template, import content'),
            'folder': (False, 'manual_create', 'Create folder manually, organize files'),
            'label': (False, 'manual_create', 'Create label manually, update text via API')
        }
        
        can_dup, method, notes = strategies.get(module_type, (False, 'unknown', 'Unknown module type'))
        
        return can_dup, method, notes
    
    def create_duplication_plan(self, source_course_id: int, 
                              target_course_ids: List[int],
                              material_types: Set[MaterialType] = None) -> DuplicationPlan:
        """
        Create a comprehensive duplication plan with manual and automated steps
        """
        
        # Analyze source course
        materials = self.analyze_course_materials(source_course_id)
        
        # Filter by material types if specified
        if material_types and MaterialType.ALL not in material_types:
            type_values = {mt.value for mt in material_types}
            materials = [m for m in materials if m.module_type in type_values]
        
        # Determine overall strategy
        automated_count = sum(1 for m in materials if m.can_duplicate)
        manual_count = len(materials) - automated_count
        
        if automated_count > manual_count:
            strategy = "hybrid_automated"
        elif manual_count > 0:
            strategy = "manual_template"
        else:
            strategy = "fully_automated"
        
        # Generate step-by-step instructions
        manual_steps, automated_steps = self._generate_duplication_steps(
            materials, source_course_id, target_course_ids
        )
        
        return DuplicationPlan(
            source_course_id=source_course_id,
            target_course_ids=target_course_ids,
            materials=materials,
            strategy=strategy,
            manual_steps=manual_steps,
            automated_steps=automated_steps
        )
    
    def _generate_duplication_steps(self, materials: List[MaterialAnalysis],
                                  source_course_id: int, 
                                  target_course_ids: List[int]) -> tuple:
        """Generate manual and automated steps for duplication"""
        
        manual_steps = []
        automated_steps = []
        
        # Group materials by duplication method
        method_groups = {}
        for material in materials:
            method = material.duplication_method
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(material)
        
        # Generate manual steps
        if 'manual_template' in method_groups:
            manual_steps.append("1. Create course template with required module types:")
            for material in method_groups['manual_template']:
                manual_steps.append(f"   - Add {material.module_type}: {material.name}")
        
        if 'manual_create' in method_groups:
            manual_steps.append("2. Manually create modules in target courses:")
            for material in method_groups['manual_create']:
                manual_steps.append(f"   - Create {material.module_type}: {material.name}")
        
        if 'manual_upload' in method_groups:
            manual_steps.append("3. Upload required files and resources:")
            for material in method_groups['manual_upload']:
                manual_steps.append(f"   - Upload files for: {material.name}")
        
        manual_steps.append("4. Use course backup/restore for bulk duplication")
        manual_steps.append("5. Verify all modules are created correctly")
        
        # Generate automated steps
        if 'forum_api' in method_groups:
            automated_steps.append("1. Use Forum APIs to duplicate forum content:")
            for material in method_groups['forum_api']:
                automated_steps.append(f"   - Duplicate forum: {material.name}")
        
        automated_steps.append("2. Update module properties via core_course_edit_module:")
        automated_steps.append("   - Update visibility settings")
        automated_steps.append("   - Update module names and descriptions")
        automated_steps.append("   - Configure module-specific settings")
        
        automated_steps.append("3. Use quiz APIs for quiz attempt management:")
        automated_steps.append("   - Configure quiz settings")
        automated_steps.append("   - Set up grading parameters")
        
        return manual_steps, automated_steps
    
    def generate_duplication_report(self, plan: DuplicationPlan) -> Dict[str, Any]:
        """Generate a comprehensive duplication report"""
        
        # Statistics
        total_materials = len(plan.materials)
        automated_count = sum(1 for m in plan.materials if m.can_duplicate)
        manual_count = total_materials - automated_count
        
        # Group by material type
        by_type = {}
        for material in plan.materials:
            mat_type = material.module_type
            if mat_type not in by_type:
                by_type[mat_type] = {'total': 0, 'automated': 0, 'manual': 0}
            
            by_type[mat_type]['total'] += 1
            if material.can_duplicate:
                by_type[mat_type]['automated'] += 1
            else:
                by_type[mat_type]['manual'] += 1
        
        # Group by duplication method
        by_method = {}
        for material in plan.materials:
            method = material.duplication_method
            if method not in by_method:
                by_method[method] = []
            by_method[method].append({
                'name': material.name,
                'type': material.module_type,
                'section': material.section_name
            })
        
        return {
            'summary': {
                'total_materials': total_materials,
                'automated_possible': automated_count,
                'manual_required': manual_count,
                'automation_rate': (automated_count / total_materials * 100) if total_materials > 0 else 0,
                'strategy': plan.strategy,
                'target_courses': len(plan.target_course_ids)
            },
            'by_material_type': by_type,
            'by_duplication_method': by_method,
            'manual_steps': plan.manual_steps,
            'automated_steps': plan.automated_steps,
            'api_limitations': {
                'unavailable_apis': [
                    'core_course_add_module',
                    'core_course_create_sections',
                    'mod_quiz_get_quiz_by_instance'
                ],
                'available_alternatives': [
                    'core_course_edit_module (for updates)',
                    'mod_forum_* (for forum management)',
                    'mod_quiz_* (for attempt management)',
                    'backup/restore (for bulk operations)'
                ]
            }
        }


def main():
    """Example usage of RevisedMaterialAnalyzer"""
    
    client = MoodleAPIClient("https://moodle.hkbu.edu.hk", "your_token")
    analyzer = RevisedMaterialAnalyzer(client)
    
    # Analyze course and create duplication plan
    plan = analyzer.create_duplication_plan(
        source_course_id=99,
        target_course_ids=[100, 101, 102],
        material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ, MaterialType.FORUM}
    )
    
    # Generate report
    report = analyzer.generate_duplication_report(plan)
    
    print("REVISED DUPLICATION PLAN")
    print("=" * 50)
    print(f"Strategy: {report['summary']['strategy']}")
    print(f"Total materials: {report['summary']['total_materials']}")
    print(f"Automated possible: {report['summary']['automated_possible']}")
    print(f"Manual required: {report['summary']['manual_required']}")
    print(f"Automation rate: {report['summary']['automation_rate']:.1f}%")
    
    print("\nMANUAL STEPS:")
    for step in plan.manual_steps:
        print(f"  {step}")
    
    print("\nAUTOMATED STEPS:")
    for step in plan.automated_steps:
        print(f"  {step}")


if __name__ == "__main__":
    main()
