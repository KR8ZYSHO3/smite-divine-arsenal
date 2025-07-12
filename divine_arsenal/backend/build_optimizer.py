"""Build Optimizer - Main interface for the build optimization system."""

from divine_arsenal.backend.advanced_build_optimizer import AdvancedBuildOptimizer

# Re-export AdvancedBuildOptimizer as BuildOptimizer for compatibility
BuildOptimizer = AdvancedBuildOptimizer

__all__ = ["BuildOptimizer"]
