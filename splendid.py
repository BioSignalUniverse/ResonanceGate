name: Veto_Check_FINAL
on: 
  push:
    branches: [ TheSplendis ] # Run every time you push code to your development branch

jobs:
  goa_test_suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Execute ITP Script
        # This executes the required integrity check script
        run: python integration_testing_protocol.py
