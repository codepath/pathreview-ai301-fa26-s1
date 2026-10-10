"""Tests for readme_scorer.py"""

import pytest

from agent.tools.readme_scorer import ReadmeScorer


@pytest.mark.unit
class TestReadmeScorer:
    """Test suite for ReadmeScorer."""

    @pytest.fixture
    def scorer(self):
        """Create a ReadmeScorer instance."""
        return ReadmeScorer()

    def test_readme_with_all_quality_signals(self, scorer):
        """Test README with all quality signals returns high score."""
        readme = """
        # Project Name
        A comprehensive project description.

        ## Installation
        ```bash
        pip install package
        ```

        ## Usage
        ```python
        import package
        package.run()
        ```

        ## Features
        - Feature 1
        - Feature 2
        - Feature 3

        ## Tech Stack
        - Python 3.9
        - FastAPI
        - PostgreSQL

        ![Build Status](https://example.com/badge.svg)
        ![Coverage](https://example.com/coverage.svg)

        ## Live Demo
        [Try it here](https://demo.example.com)

        ## Overview

        This project provides a complete example application for developers who want
        to build, configure, test, and deploy a reliable web service. The application
        is designed around a straightforward architecture that keeps components easy
        to understand and maintain. Developers can use the project as a starting point
        for local development, experimentation, integration testing, or deployment to
        a production environment. The documentation explains the major workflows so
        that new contributors can understand the project without needing detailed
        knowledge of the original implementation.

        ## Configuration

        The application can be configured for different environments using standard
        environment variables. Developers should create a local configuration before
        starting the service and provide values for database connectivity, application
        settings, and any external services used by the project. Development values
        should remain separate from production credentials. Sensitive information such
        as passwords, tokens, and private keys should never be committed to source
        control. Configuration should be reviewed whenever the application is moved
        between local, testing, staging, and production environments.

        ## Project Structure

        The project separates application code, configuration, tests, and supporting
        resources so that each responsibility remains easy to locate. Application
        modules contain the main business logic and API behavior. Database components
        manage persistence and queries. Test modules verify expected behavior and help
        prevent regressions when functionality changes. Documentation and configuration
        files provide the information required to run the project consistently across
        different environments. Contributors should follow the existing organization
        when adding new functionality so that the repository remains predictable.

        ## Development

        Start development by installing the required dependencies and confirming that
        the application runs successfully in the local environment. Changes should be
        kept focused on a specific feature, bug, or maintenance task. Developers are
        encouraged to review existing modules and tests before making modifications so
        that new code follows established patterns. When behavior changes, corresponding
        tests should be added or updated to describe the expected result. Small and
        focused changes are easier to review, test, and maintain than unrelated changes
        combined into a single update.

        ## Testing

        Automated tests are an important part of the development workflow. Run the
        relevant unit tests after modifying application behavior and verify that existing
        functionality continues to work. Tests should describe observable behavior and
        cover both successful operations and important edge cases. When fixing a bug,
        contributors should reproduce the original problem before making the change and
        then rerun the same test after the implementation. This provides clear evidence
        that the change addresses the reported behavior without introducing unnecessary
        modifications elsewhere in the project.

        ## API

        The service exposes application functionality through clearly defined endpoints.
        Clients should provide valid request data and handle both successful responses
        and expected error conditions. API behavior should remain consistent so that
        integrations do not break unexpectedly. When an endpoint changes, developers
        should update tests and documentation to reflect the new behavior. Requests
        should be validated before processing, and responses should provide enough
        information for clients to understand whether an operation succeeded or why it
        could not be completed.

        ## Deployment

        Before deployment, run the automated test suite and confirm that required
        configuration values are available in the target environment. Production
        deployments should use appropriate credentials and should not rely on local
        development settings. Teams should review logs after deployment to identify
        unexpected errors and verify that important application workflows remain
        available. If a deployment introduces a regression, the change should be
        investigated using the same reproducible testing process used during local
        development.

        ## Troubleshooting

        If the application does not start, first confirm that dependencies are installed
        and required configuration values are present. Database connectivity and service
        availability should also be checked when requests fail unexpectedly. Test output
        and application logs can provide useful information about the source of a
        problem. Reproducing an issue with a minimal set of steps makes debugging easier
        and helps contributors determine whether the problem is caused by configuration,
        application logic, external dependencies, or incorrect input.

        ## Contributing

        Contributions should be focused, tested, and documented. Before submitting a
        change, review the diff to ensure that unrelated files were not modified. Run
        the relevant tests and include enough information for another developer to
        reproduce the behavior being changed. New functionality should follow existing
        project conventions, while bug fixes should preserve unrelated behavior.
        Contributors should explain important implementation decisions when they are not
        obvious from the code and respond to review feedback with additional changes or
        clarification when necessary.

        ## Maintenance

        Regular maintenance keeps the project dependable as dependencies and development
        practices evolve. Dependencies should be reviewed periodically, tests should be
        kept aligned with current behavior, and outdated documentation should be updated.
        Refactoring should preserve externally visible behavior unless a deliberate
        behavior change is part of the task. Keeping documentation, tests, and code in
        agreement helps future contributors understand the intended behavior and reduces
        the risk of regressions during later development.
        """

        result = scorer.execute({"readme_content": readme})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is True
        assert data["word_count"] > 100
        assert data["word_count_category"] == "comprehensive"
        assert data["has_installation_section"] is True
        assert data["has_usage_section"] is True
        assert data["has_badges"] is True
        assert data["has_demo_link"] is True
        assert data["has_tech_stack_section"] is True
        assert data["overall_score"] > 0.7  # Should be high

    def test_readme_with_no_content(self, scorer):
        """Test README with no content returns score of 0.0."""
        result = scorer.execute({"readme_content": ""})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is False
        assert data["word_count"] == 0
        assert data["word_count_category"] == "minimal"
        assert data["overall_score"] == 0.0

    def test_readme_with_only_title(self, scorer):
        """Test README with only a title returns minimal word count category."""
        readme = "# Project Title"

        result = scorer.execute({"readme_content": readme})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is True
        assert data["word_count"] < 100
        assert data["word_count_category"] == "minimal"
        assert data["overall_score"] < 0.3

    def test_word_count_category_minimal(self, scorer):
        """Test word_count_category: < 100 = minimal."""
        readme = "This is a very short readme with just a few words."

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert data["word_count"] < 100
        assert data["word_count_category"] == "minimal"

    def test_word_count_category_adequate(self, scorer):
        """Test word_count_category: 100-500 = adequate."""
        readme = " ".join(["word"] * 200)  # 200 words

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert 100 <= data["word_count"] <= 500
        assert data["word_count_category"] == "adequate"

    def test_word_count_category_comprehensive(self, scorer):
        """Test word_count_category: > 500 = comprehensive."""
        readme = " ".join(["word"] * 700)  # 700 words

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert data["word_count"] > 500
        assert data["word_count_category"] == "comprehensive"

    def test_installation_section_detection(self, scorer):
        """Test detection of installation section."""
        readme_with_install = """
        # Project
        ## Installation
        pip install package
        """

        result = scorer.execute({"readme_content": readme_with_install})
        assert result.data["has_installation_section"] is True

        readme_without_install = """
        # Project
        ## Description
        This is a project.
        """

        result = scorer.execute({"readme_content": readme_without_install})
        assert result.data["has_installation_section"] is False

    def test_usage_section_detection(self, scorer):
        """Test detection of usage section."""
        readme_with_usage = """
        # Project
        ## Usage
        Run the project like this...
        """

        result = scorer.execute({"readme_content": readme_with_usage})
        assert result.data["has_usage_section"] is True

    def test_setup_keyword_counts_as_installation(self, scorer):
        """Test that 'setup' keyword counts as installation."""
        readme = """
        # Project
        ## Getting Started
        Run setup.sh
        """

        result = scorer.execute({"readme_content": readme})
        # "Getting Started" matches the pattern
        assert (
            result.data["has_installation_section"] is True
            or result.data["has_usage_section"] is True
        )

    def test_quickstart_counts_as_usage(self, scorer):
        """Test that 'quickstart' counts as usage."""
        readme = """
        # Project
        ## Quickstart
        Quick example here
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_usage_section"] is True

    def test_badge_detection(self, scorer):
        """Test badge detection."""
        readme_with_badges = """
        ![Status](https://example.com/status.svg)
        ![License](https://example.com/license.svg)
        """

        result = scorer.execute({"readme_content": readme_with_badges})
        assert result.data["has_badges"] is True

    def test_demo_link_detection(self, scorer):
        """Test demo/live link detection."""
        readme_with_demo = """
        # Project
        [Live Demo](https://demo.example.com)
        """

        result = scorer.execute({"readme_content": readme_with_demo})
        assert result.data["has_demo_link"] is True

    def test_tech_stack_section_detection(self, scorer):
        """Test tech stack section detection."""
        readme_with_stack = """
        # Project
        ## Tech Stack
        - Python
        - FastAPI
        - PostgreSQL
        """

        result = scorer.execute({"readme_content": readme_with_stack})
        assert result.data["has_tech_stack_section"] is True

    def test_technologies_keyword_counts(self, scorer):
        """Test that 'Technologies' keyword counts as tech stack."""
        readme = """
        # Project
        ## Technologies
        Python, JavaScript, React
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_tech_stack_section"] is True

    def test_overall_score_calculation(self, scorer):
        """Test that overall score aggregates components."""
        readme = """
        # Good README

        ## Installation
        Install it!

        ## Usage
        Use it!

        ## Tech Stack
        Python, JavaScript

        ![Build](https://example.com/build.svg)

        This readme has lots of content here.
        """ * 3  # Make it comprehensive

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert 0.0 <= data["overall_score"] <= 1.0
        # Multiple signals should yield higher score
        assert data["overall_score"] > 0.5

    def test_missing_readme_content_key(self, scorer):
        """Test handling of missing readme_content key."""
        result = scorer.execute({})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is False

    def test_result_has_all_required_fields(self, scorer):
        """Test that result has all required fields."""
        result = scorer.execute({"readme_content": "# Test"})

        data = result.data
        assert "has_readme" in data
        assert "word_count" in data
        assert "word_count_category" in data
        assert "has_installation_section" in data
        assert "has_usage_section" in data
        assert "has_badges" in data
        assert "has_demo_link" in data
        assert "has_tech_stack_section" in data
        assert "overall_score" in data

    def test_case_insensitive_section_detection(self, scorer):
        """Test that section detection is case insensitive."""
        readme = """
        # Project
        ## INSTALLATION
        Install here
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_installation_section"] is True

    def test_whitespace_only_readme(self, scorer):
        """Test handling of whitespace-only README."""
        result = scorer.execute({"readme_content": "   \n\n   \t  "})

        data = result.data
        assert data["has_readme"] is False
        assert data["word_count"] == 0

    def test_example_keyword_counts_as_usage(self, scorer):
        """Test that 'Example' counts as usage section."""
        readme = """
        # Project
        ## Example
        Here's how to use it
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_usage_section"] is True

    def test_score_scales_with_word_count(self, scorer):
        """Test that longer READMEs get bonus in score."""
        short_readme = "# Title\nSmall content."
        long_readme = "# Title\n" + "Content paragraph. " * 100

        result_short = scorer.execute({"readme_content": short_readme})
        result_long = scorer.execute({"readme_content": long_readme})

        assert result_long.data["overall_score"] > result_short.data["overall_score"]

    def test_try_it_as_demo_indicator(self, scorer):
        """Test that 'try it' indicates demo link."""
        readme = "Check it out [try it here](https://example.com)"

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_demo_link"] is True

    def test_built_with_counts_as_tech_stack(self, scorer):
        """Test that 'Built With' counts as tech stack."""
        readme = """
        # Project
        ## Built With
        - Python
        - FastAPI
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_tech_stack_section"] is True
