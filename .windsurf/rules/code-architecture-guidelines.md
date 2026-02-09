---
trigger: model_decision
description: "Scaffold new projects using a walking skeleton approach."
---
# Walking skeleton architecture principles

- Build a minimal end-to-end system that wires together frontend, backend, database, and CI/CD from the start.
- Ensure the skeleton is deployable from day one, even with placeholder logic.
- Use real systems and interfaces (e.g., HTTP servers, routers, file storage) with stubbed logic.
- Avoid one-off logic or fake architecture that will require rewrites.
- Verify full request flow through all layers early in development.
- Design modules to be independently replaceable and evolvable.
- Include basic logging, error handling, and health checks from the beginning.

