"""
Test script for ImpactGuard
Demonstrates the system's capabilities
"""
import json
from pathlib import Path
from services import ImpactService
from models import ChangeInput, FileChange


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_basic_analysis():
    """Test basic impact analysis"""
    print_section("TEST 1: Basic Impact Analysis")
    
    # Use current directory as test repository
    repo_path = str(Path.cwd())
    print(f"Repository: {repo_path}")
    
    # Initialize service
    service = ImpactService(repo_path)
    
    # Test with some files from the project
    test_files = ["main.py", "config.py", "models.py"]
    
    print(f"\nAnalyzing files: {', '.join(test_files)}")
    
    try:
        report = service.analyze_specific_files(test_files)
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"\nRisk Level: {report.risk_level.value}")
        print(f"Risk Score: {report.risk_score:.2f}")
        print(f"Affected Areas: {', '.join(report.affected_areas) if report.affected_areas else 'None'}")
        print(f"Critical Files: {len(report.critical_files)}")
        print(f"Warnings: {len(report.warnings)}")
        print(f"Suggested Reviewers: {len(report.suggested_reviewers)}")
        print(f"Learning Path Items: {len(report.learning_path)}")
        
        return report
    
    except Exception as e:
        print(f"\n✗ Analysis failed: {str(e)}")
        return None


def test_detailed_report(report):
    """Display detailed report information"""
    if not report:
        return
    
    print_section("TEST 2: Detailed Report")
    
    # Display warnings
    if report.warnings:
        print("\nWarnings:")
        for i, warning in enumerate(report.warnings[:3], 1):
            print(f"  {i}. [{warning.severity.upper()}] {warning.message}")
    
    # Display suggested reviewers
    if report.suggested_reviewers:
        print("\nSuggested Reviewers:")
        for reviewer in report.suggested_reviewers[:3]:
            print(f"  • {reviewer.name} (Confidence: {reviewer.confidence:.2f})")
            if reviewer.expertise_areas:
                print(f"    Expertise: {', '.join(reviewer.expertise_areas)}")
    
    # Display learning path
    if report.learning_path:
        print("\nLearning Path:")
        for i, item in enumerate(report.learning_path[:5], 1):
            print(f"  {i}. {item.file}")
            print(f"     Reason: {item.reason}")
            print(f"     Importance: {item.importance.upper()}")


def test_voice_summary(report):
    """Test voice summary generation"""
    if not report:
        return
    
    print_section("TEST 3: Voice Summary")
    
    if report.voice_summary:
        print("\nVoice Summary:")
        print(f'"{report.voice_summary}"')
        print(f"\nLength: {len(report.voice_summary)} characters")
        print(f"Estimated speaking time: ~{len(report.voice_summary.split()) / 2.5:.1f} seconds")
    else:
        print("\nVoice summary not available")


def test_json_output(report):
    """Test JSON serialization"""
    if not report:
        return
    
    print_section("TEST 4: JSON Output")
    
    try:
        # Convert to dict
        report_dict = report.dict()
        
        # Pretty print JSON
        json_output = json.dumps(report_dict, indent=2, default=str)
        
        print("\nJSON Output (first 500 characters):")
        print(json_output[:500] + "...")
        
        print(f"\nTotal JSON size: {len(json_output)} characters")
        
    except Exception as e:
        print(f"\n✗ JSON serialization failed: {str(e)}")


def test_quick_summary():
    """Test quick summary feature"""
    print_section("TEST 5: Quick Summary")
    
    repo_path = str(Path.cwd())
    service = ImpactService(repo_path)
    
    test_files = ["main.py", "models.py"]
    
    try:
        report = service.analyze_specific_files(test_files)
        summary = service.get_quick_summary(report)
        
        print("\nQuick Summary:")
        print(summary)
        
    except Exception as e:
        print(f"\n✗ Summary generation failed: {str(e)}")


def test_change_input():
    """Test with ChangeInput model"""
    print_section("TEST 6: ChangeInput Model")
    
    repo_path = str(Path.cwd())
    service = ImpactService(repo_path)
    
    # Create change input with file changes
    change_input = ChangeInput(
        repository_path=repo_path,
        changed_files=[
            FileChange(path="main.py", additions=50, deletions=10),
            FileChange(path="config.py", additions=5, deletions=2)
        ],
        branch="main"
    )
    
    print(f"\nRepository: {change_input.repository_path}")
    print(f"Changed files: {len(change_input.changed_files)}")
    print(f"Branch: {change_input.branch}")
    
    try:
        report = service.analyze_impact(change_input)
        print(f"\n✓ Analysis completed!")
        print(f"Risk Level: {report.risk_level.value}")
        print(f"Risk Score: {report.risk_score:.2f}")
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {str(e)}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  ImpactGuard Test Suite")
    print("=" * 60)
    print("\nThis script demonstrates ImpactGuard's capabilities")
    print("using the current project as a test repository.")
    
    # Run tests
    report = test_basic_analysis()
    test_detailed_report(report)
    test_voice_summary(report)
    test_json_output(report)
    test_quick_summary()
    test_change_input()
    
    print("\n" + "=" * 60)
    print("  Test Suite Completed")
    print("=" * 60)
    print("\nNote: Some features may not work fully without a proper")
    print("git repository with commit history.")
    print("\nTo test with a real repository:")
    print("  1. Navigate to a git repository")
    print("  2. Run: python test_impact_guard.py")
    print("  3. Or use the API: python main.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

# Made with Bob
