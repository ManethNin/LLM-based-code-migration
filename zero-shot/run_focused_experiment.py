#!/usr/bin/env python3
"""
Focused experiment runner for testing specific projects or project types.
This gives you more control over which projects to test and how many.
"""

import argparse
import logging
from pathlib import Path
from groq_pipeline_experiment import test_project_with_pipeline, GroqExperimentResults
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def list_available_projects():
    """List all available projects in the dataset."""
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print("❌ Dataset directory not found")
        return []
    
    projects = []
    for project_dir in sorted(dataset_dir.iterdir()):
        if project_dir.is_dir():
            # Try to load basic info
            try:
                from groq_pipeline_experiment import load_dataset_entry
                entry = load_dataset_entry(project_dir)
                projects.append({
                    'hash': project_dir.name,
                    'repo': entry.repo_slug,
                    'dependency': entry.version_upgrade_str,
                    'path': project_dir
                })
            except Exception as e:
                logger.warning(f"Could not load {project_dir.name}: {e}")
    
    return projects

def run_focused_experiment(project_hashes=None, max_projects=None, dependency_filter=None):
    """Run experiment on specific projects or with filters."""
    
    print("🎯 FOCUSED GROQ EXPERIMENT")
    print("=" * 50)
    
    # Get available projects
    all_projects = list_available_projects()
    
    if not all_projects:
        print("❌ No projects found")
        return
    
    # Apply filters
    selected_projects = all_projects
    
    if project_hashes:
        selected_projects = [p for p in selected_projects if p['hash'] in project_hashes]
        print(f"🔍 Filtering to specific projects: {len(selected_projects)} selected")
    
    if dependency_filter:
        selected_projects = [p for p in selected_projects if dependency_filter.lower() in p['dependency'].lower()]
        print(f"🔍 Filtering by dependency '{dependency_filter}': {len(selected_projects)} selected")
    
    if max_projects:
        selected_projects = selected_projects[:max_projects]
        print(f"🔢 Limiting to first {max_projects} projects")
    
    if not selected_projects:
        print("❌ No projects match the criteria")
        return
    
    print(f"\\n📋 Selected {len(selected_projects)} projects:")
    for i, project in enumerate(selected_projects, 1):
        print(f"  {i}. {project['repo']} ({project['hash'][:8]}...)")
        print(f"     🔧 {project['dependency']}")
    
    print("\\n" + "=" * 50)
    
    # Run experiments
    results = GroqExperimentResults()
    experiment_name = f"focused-experiment-{len(selected_projects)}projects"
    
    for i, project in enumerate(selected_projects, 1):
        print(f"\\n🔄 [{i}/{len(selected_projects)}] Processing: {project['repo']}")
        
        result = test_project_with_pipeline(project['path'], experiment_name)
        results.add_result(project['hash'], result)
        
        # Rate limiting between requests
        if i < len(selected_projects):
            time.sleep(2)
    
    # Results summary
    print(f"\\n{'='*50}")
    print("🎯 EXPERIMENT RESULTS")
    print(f"{'='*50}")
    
    summary = results.summary
    total = summary["total_projects"]
    
    print(f"📊 Total projects: {total}")
    print(f"✅ Diffs generated: {summary['successful_diffs']}/{total} ({summary['successful_diffs']/total*100:.1f}%)")
    print(f"🔧 Compilation success: {summary['compilation_success']}/{total} ({summary['compilation_success']/total*100:.1f}%)")
    print(f"🧪 Test success: {summary['test_success']}/{total} ({summary['test_success']/total*100:.1f}%)")
    
    # Success cases
    if summary['compilation_success'] > 0:
        print(f"\\n🎉 SUCCESSFUL COMPILATIONS:")
        # Fix: results.results is a list, not dict
        successful_results = [r for r in results.results if r.get('compilation_success', False)]
        for i, result in enumerate(successful_results, 1):
            print(f"  ✅ Success #{i}: Compilation and tests passed!")
    
    # Save results
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"focused_experiment_{timestamp}.json"
    results.save_results(filename)
    print(f"\\n💾 Results saved to: {filename}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Run focused Groq experiments")
    parser.add_argument("--projects", nargs="+", help="Specific project hashes to test")
    parser.add_argument("--max", type=int, help="Maximum number of projects to test")
    parser.add_argument("--dependency", help="Filter by dependency name (e.g., 'mysql', 'thrift')")
    parser.add_argument("--list", action="store_true", help="List all available projects")
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available Projects:")
        print("=" * 60)
        projects = list_available_projects()
        for i, project in enumerate(projects, 1):
            print(f"{i:2d}. {project['repo']:<30} ({project['hash'][:8]}...)")
            print(f"    🔧 {project['dependency']}")
            print()
        print(f"Total: {len(projects)} projects")
        return
    
    # Run focused experiment
    run_focused_experiment(
        project_hashes=args.projects,
        max_projects=args.max,
        dependency_filter=args.dependency
    )

if __name__ == "__main__":
    main()
