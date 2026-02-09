---
trigger: model_decision
description: "Encourage early automation of CI/CD pipelines and deploy environments."
---
# CI/CD and deployment automation rules

- Automate the deployment pipeline early in development.
- Ensure every code change is deployable to a real (even test) environment.
- Run all tests on every push to detect regressions early.
- Use `.env` or config files with environment variables for secrets and runtime behavior.
- Monitor application health with basic checks and logs in all environments.
- Use scripts or build tools (`Makefile`, `npm run`, `justfile`) for repeated tasks.
- Keep CI workflows fast and deterministic to support rapid iteration.

