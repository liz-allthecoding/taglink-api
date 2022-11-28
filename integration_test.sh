. .venv-integration-tests/bin/activate
TEST_ENV=local python -m pytest -s integration_tests
deactivate
