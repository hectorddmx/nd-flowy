"""
Workflowy Flow Dagger CI/CD Pipeline

This pipeline provides containerized CI/CD for the Workflowy Flow application.
Run with: dagger call ci --source=.

Available commands:
- dagger call lint --source=.
- dagger call test --source=.
- dagger call build --source=.
- dagger call ci --source=.
"""

import dagger
from dagger import dag, function, object_type


@object_type
class WorkflowyFlow:
    """CI/CD pipeline for Workflowy Flow application."""

    @function
    def python_base(self) -> dagger.Container:
        """
        Create a base container with Python and uv installed.

        Uses Python 3.12 slim image with uv for fast dependency management.
        """
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "--no-cache-dir", "uv"])
        )

    def _python_container_with_deps(
        self,
        source: dagger.Directory,
        include_dev: bool = True,
        for_testing: bool = False,
    ) -> dagger.Container:
        """
        Create a Python container with dependencies installed.

        Args:
            source: The source directory
            include_dev: If True, include dev dependencies (for testing/linting)
            for_testing: If True, set environment variables for testing
        """
        sync_cmd = ["uv", "sync", "--frozen", "--no-cache"]
        if include_dev:
            sync_cmd.append("--all-extras")

        container = (
            self.python_base()
            .with_directory("/app", source)
            .with_workdir("/app")
        )

        # Set test environment variables if needed
        if for_testing:
            container = (
                container
                .with_env_variable("WF_API_KEY", "test-api-key-not-real")
                .with_env_variable("WF_API_BASE_URL", "https://workflowy.com/api/v1")
            )

        return container.with_exec(sync_cmd)

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """
        Run linting with ruff (check + format validation).

        Checks Python code style and formatting in app/ and tests/ directories.
        """
        lint_container = (
            self._python_container_with_deps(source)
            .with_exec(["uv", "run", "ruff", "check", "app/", "tests/"])
            .with_exec(["uv", "run", "ruff", "format", "--check", "app/", "tests/"])
        )

        return await lint_container.stdout()

    @function
    async def format(self, source: dagger.Directory) -> str:
        """
        Format code with ruff (modifies files).

        Returns formatted source directory.
        """
        format_container = (
            self._python_container_with_deps(source)
            .with_exec(["uv", "run", "ruff", "format", "app/", "tests/"])
            .with_exec(["uv", "run", "ruff", "check", "app/", "tests/", "--fix"])
        )

        return await format_container.stdout()

    @function
    async def test(
        self,
        source: dagger.Directory,
        show_verbose: bool = True,
        coverage: bool = False,
    ) -> str:
        """
        Run pytest tests.

        Args:
            source: The source directory
            show_verbose: If True, show verbose output
            coverage: If True, generate coverage report
        """
        pytest_cmd = ["uv", "run", "pytest", "tests/"]

        if show_verbose:
            pytest_cmd.append("-v")

        pytest_cmd.append("--tb=short")

        if coverage:
            pytest_cmd.extend([
                "--cov=app",
                "--cov-report=term-missing",
            ])

        test_container = (
            self._python_container_with_deps(source, for_testing=True)
            .with_exec(pytest_cmd)
        )

        return await test_container.stdout()

    @function
    async def build(self, source: dagger.Directory) -> dagger.Directory:
        """
        Build Python package with uv.

        Returns the built directory with dist/ containing the wheel.
        """
        build_container = (
            self._python_container_with_deps(source, include_dev=False)
            .with_exec(["uv", "build"])
        )

        return build_container.directory("/app")

    @function
    async def build_and_verify(self, source: dagger.Directory) -> str:
        """
        Build and verify the output.

        Returns a summary of the build including file listings.
        """
        build_result = await self.build(source)

        verify_container = (
            dag.container()
            .from_("alpine:latest")
            .with_directory("/build", build_result)
            .with_workdir("/build")
            .with_exec(["sh", "-c", """
                echo "=== Build Verification ==="
                echo ""
                echo "Project structure:"
                ls -la
                echo ""
                echo "Distribution files:"
                ls -la dist/ 2>/dev/null || echo "No dist/ directory"
                echo ""
                echo "Build complete!"
            """])
        )

        return await verify_container.stdout()

    def _extract_issues(self, output: str, stage_name: str) -> list[str]:
        """Extract warnings, errors, and issues from stage output."""
        issues = []
        lines = output.split('\n')

        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower or line_lower.startswith('===') or line_lower.startswith('---'):
                continue

            if 'passed' in line_lower or 'skipping' in line_lower:
                continue

            # Pytest failures
            if 'failed' in line_lower and 'passed' not in line_lower:
                issues.append(f"  {line.strip()}")

            # Ruff issues
            elif line.strip().startswith('app/') or line.strip().startswith('tests/'):
                if ':' in line:
                    issues.append(f"  {line.strip()}")

            # Generic error patterns
            elif ('error:' in line_lower or 'Error:' in line) and '0 error' not in line_lower:
                issues.append(f"  {line.strip()}")

        return issues[:20]

    def _format_summary(
        self,
        title: str,
        stage_results: list[tuple[str, bool, str, str]],
    ) -> str:
        """Format a summary table for CI stages with bundled warnings/errors."""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append(f"  {title} SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"{'Stage':<25} {'Status':<12} {'Issues'}")
        lines.append("-" * 60)

        has_failures = False
        all_issues: list[tuple[str, list[str]]] = []

        for name, passed, error_msg, output in stage_results:
            issues = self._extract_issues(output, name) if output else []
            issue_count = len(issues)

            if passed:
                status = "PASS"
                if issue_count > 0:
                    status = "WARN"
            else:
                status = "FAIL"
                has_failures = True

            issue_text = f"{issue_count} issues" if issue_count > 0 else ""
            lines.append(f"{name:<25} {status:<12} {issue_text}")

            if issues:
                all_issues.append((name, issues))

        lines.append("-" * 60)

        if all_issues:
            lines.append("")
            lines.append("ISSUES FOUND:")
            lines.append("")
            for stage_name, issues in all_issues:
                lines.append(f"> {stage_name}:")
                for issue in issues[:10]:
                    lines.append(issue)
                if len(issues) > 10:
                    lines.append(f"  ... and {len(issues) - 10} more")
                lines.append("")

        if has_failures:
            lines.append(f"RESULT: {title} FAILED - Fix errors above and re-run")
        elif all_issues:
            lines.append(f"RESULT: {title} PASSED WITH WARNINGS")
        else:
            lines.append(f"RESULT: {title} PASSED - All stages completed successfully!")

        lines.append("=" * 60)
        return "\n".join(lines)

    @function
    async def ci(
        self,
        source: dagger.Directory,
        skip_build: bool = False,
        coverage: bool = False,
    ) -> str:
        """
        Run full CI pipeline: lint, test, build.

        Args:
            source: The source directory
            skip_build: If True, skip the build step (faster CI)
            coverage: If True, generate coverage report during tests
        """
        results = []
        stage_results: list[tuple[str, bool, str, str]] = []

        # Lint
        results.append("=== Linting (ruff check + format) ===")
        try:
            lint_result = await self.lint(source)
            results.append(lint_result)
            results.append("Linting passed!")
            stage_results.append(("Lint (ruff)", True, "", lint_result))
        except Exception as e:
            error_msg = str(e).split("[traceparent")[0].strip()
            results.append(f"Linting failed: {error_msg}")
            stage_results.append(("Lint (ruff)", False, error_msg, ""))

        # Test
        results.append("\n=== Testing (pytest) ===")
        try:
            test_result = await self.test(source, coverage=coverage)
            results.append(test_result)
            results.append("Tests passed!")
            stage_results.append(("Test (pytest)", True, "", test_result))
        except Exception as e:
            error_msg = str(e).split("[traceparent")[0].strip()
            results.append(f"Tests failed: {error_msg}")
            stage_results.append(("Test (pytest)", False, error_msg, ""))

        # Build (optional)
        if not skip_build:
            results.append("\n=== Building (uv build) ===")
            try:
                build_result = await self.build_and_verify(source)
                results.append(build_result)
                results.append("Build succeeded!")
                stage_results.append(("Build (uv)", True, "", build_result))
            except Exception as e:
                error_msg = str(e).split("[traceparent")[0].strip()
                results.append(f"Build failed: {error_msg}")
                stage_results.append(("Build (uv)", False, error_msg, ""))
        else:
            results.append("\n=== Build Skipped ===")
            stage_results.append(("Build (uv)", True, "skipped", ""))

        # Summary
        results.append(self._format_summary("CI PIPELINE", stage_results))
        return "\n".join(results)

    @function
    async def ci_quick(self, source: dagger.Directory) -> str:
        """
        Run quick CI (lint + test only, no build).

        This is the fastest CI option for rapid feedback.
        """
        return await self.ci(source, skip_build=True)
