import pytest
from unittest.mock import Mock, patch
from app.services.template_service import TemplateService
from app.services.variable_substitution import VariableSubstitutionService
from app.models.template import Template


class TestTemplateService:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def template_service(self, mock_db):
        return TemplateService(mock_db)

    @pytest.fixture
    def sample_template(self):
        return Template(
            id="test-template",
            name="Test Template",
            subject="Welcome {{user_name}}",
            body="<h1>Hello {{user_name}}!</h1><p>Welcome to {{company}}</p>",
            language="en"
        )

    def test_create_template(self, template_service, mock_db, sample_template):
        """Test template creation"""
        # Mock the repository methods
        mock_repo = Mock()
        mock_repo.create_template.return_value = sample_template
        mock_repo.get_latest_version_number.return_value = 0

        template_service.template_repo = mock_repo
        template_service.version_repo = Mock()

        result = template_service.create_template({
            "name": "Test Template",
            "subject": "Welcome {{user_name}}",
            "body": "<h1>Hello {{user_name}}!</h1><p>Welcome to {{company}}</p>",
            "language": "en"
        })

        assert result == sample_template
        mock_repo.create_template.assert_called_once()

    def test_get_template_with_cache_hit(self, template_service, mock_db, sample_template):
        """Test template retrieval with cache hit"""
        with patch.object(template_service.cache_service, 'get') as mock_cache_get:
            mock_cache_get.return_value = sample_template

            result = template_service.get_template("test-template")

            assert result == sample_template
            mock_cache_get.assert_called_once_with("template:test-template")
            # Should not call repository when cache hit
            template_service.template_repo.get_template.assert_not_called()

    def test_get_template_cache_miss(self, template_service, mock_db, sample_template):
        """Test template retrieval with cache miss"""
        with patch.object(template_service.cache_service, 'get') as mock_cache_get, \
             patch.object(template_service.cache_service, 'set') as mock_cache_set:

            mock_cache_get.return_value = None
            template_service.template_repo.get_template.return_value = sample_template

            result = template_service.get_template("test-template")

            assert result == sample_template
            mock_cache_get.assert_called_once_with("template:test-template")
            mock_cache_set.assert_called_once()

    def test_render_template_success(self, template_service, mock_db, sample_template):
        """Test successful template rendering"""
        variables = {"user_name": "John", "company": "TestCo"}

        with patch.object(template_service, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_template

            result = template_service.render_template("test-template", variables)

            assert result is not None
            assert "John" in result["body"]
            assert "TestCo" in result["body"]
            assert result["subject"] == "Welcome John"

    def test_render_template_not_found(self, template_service, mock_db):
        """Test template rendering when template not found"""
        with patch.object(template_service, 'get_template') as mock_get_template:
            mock_get_template.return_value = None

            result = template_service.render_template("nonexistent", {})

            assert result is None


class TestVariableSubstitutionService:
    @pytest.fixture
    def substitution_service(self):
        return VariableSubstitutionService()

    def test_substitute_simple_variables(self, substitution_service):
        """Test basic variable substitution"""
        template = "Hello {{name}}, welcome to {{company}}!"
        variables = {"name": "John", "company": "TestCo"}

        result = substitution_service.substitute(template, variables)

        assert result == "Hello John, welcome to TestCo!"

    def test_substitute_missing_variables(self, substitution_service):
        """Test substitution with missing variables"""
        template = "Hello {{name}}, welcome to {{company}}!"
        variables = {"name": "John"}

        result = substitution_service.substitute(template, variables)

        assert result == "Hello John, welcome to {{company}}!"

    def test_substitute_no_variables(self, substitution_service):
        """Test template with no variables"""
        template = "Hello World!"
        variables = {}

        result = substitution_service.substitute(template, variables)

        assert result == "Hello World!"

    def test_substitute_special_characters(self, substitution_service):
        """Test substitution with special characters"""
        template = "Price: ${{price}}"
        variables = {"price": "99.99"}

        result = substitution_service.substitute(template, variables)

        assert result == "Price: $99.99"
