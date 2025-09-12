"""
Test Material Duplication Manager

Tests for the MaterialDuplicationManager functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path.resolve()))

from src.moodle_client import MoodleAPIClient
from src.material_duplicator import (
    MaterialDuplicationManager, 
    DuplicationJob, 
    MaterialType,
    DuplicationResult
)


class TestMaterialDuplicationManager(unittest.TestCase):
    
    def setUp(self):
        self.mock_client = Mock(spec=MoodleAPIClient)
        self.manager = MaterialDuplicationManager(self.mock_client)
    
    def test_get_course_materials_basic(self):
        """Test getting course materials"""
        # Mock course contents
        mock_contents = [
            {
                'section': 0,
                'name': 'General',
                'modules': [
                    {
                        'id': 1,
                        'name': 'Assignment 1',
                        'modname': 'assign',
                        'visible': True
                    },
                    {
                        'id': 2,
                        'name': 'Quiz 1',
                        'modname': 'quiz',
                        'visible': True
                    }
                ]
            },
            {
                'section': 1,
                'name': 'Week 1',
                'modules': [
                    {
                        'id': 3,
                        'name': 'Forum Discussion',
                        'modname': 'forum',
                        'visible': False
                    }
                ]
            }
        ]
        
        self.mock_client.get_course_contents.return_value = mock_contents
        
        # Test getting all materials
        materials = self.manager.get_course_materials(99)
        
        # Should get 2 visible materials (assignment and quiz)
        self.assertEqual(len(materials), 2)
        self.assertEqual(materials[0]['name'], 'Assignment 1')
        self.assertEqual(materials[1]['name'], 'Quiz 1')
        
        # Test including hidden materials
        materials_with_hidden = self.manager.get_course_materials(99, include_hidden=True)
        self.assertEqual(len(materials_with_hidden), 3)
    
    def test_get_course_materials_filtered(self):
        """Test getting filtered course materials"""
        mock_contents = [
            {
                'section': 0,
                'name': 'General',
                'modules': [
                    {'id': 1, 'name': 'Assignment 1', 'modname': 'assign', 'visible': True},
                    {'id': 2, 'name': 'Quiz 1', 'modname': 'quiz', 'visible': True},
                    {'id': 3, 'name': 'Forum 1', 'modname': 'forum', 'visible': True}
                ]
            }
        ]
        
        self.mock_client.get_course_contents.return_value = mock_contents
        
        # Test filtering by assignment type only
        materials = self.manager.get_course_materials(
            99, 
            material_types={MaterialType.ASSIGNMENT}
        )
        
        self.assertEqual(len(materials), 1)
        self.assertEqual(materials[0]['modname'], 'assign')
    
    def test_duplicate_material_to_course_success(self):
        """Test successful material duplication"""
        source_material = {
            'id': 1,
            'name': 'Test Assignment',
            'modname': 'assign',
            'visible': True
        }
        
        # Mock successful API response
        self.mock_client.add_module.return_value = {
            'cmid': 100,
            'instance': 50,
            'warnings': []
        }
        
        result = self.manager.duplicate_material_to_course(
            source_material, 
            target_course_id=200,
            target_section=1
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.source_module_id, 1)
        self.assertEqual(result.target_course_id, 200)
        self.assertEqual(result.target_module_id, 100)
        self.assertEqual(result.material_name, 'Test Assignment')
        self.assertEqual(result.material_type, 'assign')
    
    def test_duplicate_material_to_course_failure(self):
        """Test failed material duplication"""
        source_material = {
            'id': 1,
            'name': 'Test Assignment',
            'modname': 'assign',
            'visible': True
        }
        
        # Mock API failure
        self.mock_client.add_module.side_effect = Exception("API Error")
        
        result = self.manager.duplicate_material_to_course(
            source_material,
            target_course_id=200,
            target_section=1
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "API Error")
        self.assertIsNone(result.target_module_id)
    
    def test_prepare_module_data_assignment(self):
        """Test preparing assignment module data"""
        source_material = {
            'id': 1,
            'name': 'Test Assignment',
            'modname': 'assign',
            'visible': True
        }
        
        module_data = self.manager._prepare_module_data(source_material, 1)
        
        self.assertEqual(module_data['modulename'], 'assign')
        self.assertEqual(module_data['section'], 1)
        self.assertEqual(module_data['name'], 'Test Assignment')
        self.assertEqual(module_data['visible'], True)
        self.assertIn('intro', module_data)
    
    def test_prepare_module_data_quiz(self):
        """Test preparing quiz module data"""
        source_material = {
            'id': 2,
            'name': 'Test Quiz',
            'modname': 'quiz',
            'visible': True
        }
        
        module_data = self.manager._prepare_module_data(source_material, 2)
        
        self.assertEqual(module_data['modulename'], 'quiz')
        self.assertEqual(module_data['section'], 2)
        self.assertIn('grade', module_data)
        self.assertIn('attempts', module_data)
    
    def test_duplicate_materials_bulk(self):
        """Test bulk material duplication"""
        # Mock course contents
        mock_contents = [
            {
                'section': 0,
                'name': 'General',
                'modules': [
                    {'id': 1, 'name': 'Assignment 1', 'modname': 'assign', 'visible': True},
                    {'id': 2, 'name': 'Quiz 1', 'modname': 'quiz', 'visible': True}
                ]
            }
        ]
        
        self.mock_client.get_course_contents.return_value = mock_contents
        self.mock_client.add_module.return_value = {'cmid': 100, 'instance': 50}
        
        # Create duplication job
        job = DuplicationJob(
            source_course_id=99,
            target_course_ids=[200, 201],
            material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ}
        )
        
        results = self.manager.duplicate_materials_bulk(job)
        
        # Should have 4 results (2 materials × 2 target courses)
        self.assertEqual(len(results), 4)
        
        # All should be successful
        successful_results = [r for r in results if r.success]
        self.assertEqual(len(successful_results), 4)
        
        # Verify API calls
        self.assertEqual(self.mock_client.add_module.call_count, 4)
    
    def test_generate_duplication_report(self):
        """Test duplication report generation"""
        results = [
            DuplicationResult(1, 200, 100, True, material_type='assign', material_name='Assignment 1'),
            DuplicationResult(2, 200, 101, True, material_type='quiz', material_name='Quiz 1'),
            DuplicationResult(1, 201, 102, True, material_type='assign', material_name='Assignment 1'),
            DuplicationResult(2, 201, None, False, error_message='API Error', material_type='quiz', material_name='Quiz 1')
        ]
        
        report = self.manager.generate_duplication_report(results)
        
        # Check summary
        self.assertEqual(report['summary']['total_operations'], 4)
        self.assertEqual(report['summary']['successful'], 3)
        self.assertEqual(report['summary']['failed'], 1)
        self.assertEqual(report['summary']['success_rate'], 75.0)
        
        # Check by course breakdown
        self.assertEqual(report['by_course'][200]['success'], 2)
        self.assertEqual(report['by_course'][200]['failed'], 0)
        self.assertEqual(report['by_course'][201]['success'], 1)
        self.assertEqual(report['by_course'][201]['failed'], 1)
        
        # Check by material type
        self.assertEqual(report['by_material_type']['assign']['success'], 2)
        self.assertEqual(report['by_material_type']['assign']['failed'], 0)
        self.assertEqual(report['by_material_type']['quiz']['success'], 1)
        self.assertEqual(report['by_material_type']['quiz']['failed'], 1)
        
        # Check failed operations
        self.assertEqual(len(report['failed_operations']), 1)
        self.assertEqual(report['failed_operations'][0]['material_name'], 'Quiz 1')
        self.assertEqual(report['failed_operations'][0]['error'], 'API Error')


class TestDuplicationJob(unittest.TestCase):
    
    def test_duplication_job_creation(self):
        """Test creating a duplication job"""
        job = DuplicationJob(
            source_course_id=99,
            target_course_ids=[100, 101, 102],
            material_types={MaterialType.ASSIGNMENT, MaterialType.QUIZ},
            section_mapping={0: 1, 1: 2},
            include_hidden=False,
            preserve_dates=True
        )
        
        self.assertEqual(job.source_course_id, 99)
        self.assertEqual(len(job.target_course_ids), 3)
        self.assertIn(MaterialType.ASSIGNMENT, job.material_types)
        self.assertIn(MaterialType.QUIZ, job.material_types)
        self.assertEqual(job.section_mapping[0], 1)
        self.assertFalse(job.include_hidden)
        self.assertTrue(job.preserve_dates)


class TestMaterialType(unittest.TestCase):
    
    def test_material_type_enum(self):
        """Test MaterialType enum values"""
        self.assertEqual(MaterialType.ASSIGNMENT.value, 'assign')
        self.assertEqual(MaterialType.QUIZ.value, 'quiz')
        self.assertEqual(MaterialType.FORUM.value, 'forum')
        self.assertEqual(MaterialType.ALL.value, 'all')


if __name__ == '__main__':
    unittest.main()
