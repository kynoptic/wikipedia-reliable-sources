# Source code for custom rules

This directory contains the source code for the custom `markdownlint` rules used in this project.

## Important notes

* **Module format:** All rules are written using modern ES Modules (ESM) syntax (`import`/`export`).
* **Not for direct use:** These source files are **not** directly consumable by the `markdownlint` VS Code extension or `markdownlint-cli2`, which expect CommonJS modules.
* **Build required:** Before these rules can be used, they must be transpiled into CommonJS format. Run the following command from the project root:

    ```bash
    npm run build
    ```

This will place the compiled, ready-to-use rule files into the `dist/` directory.

For more details on the development workflow and how to use the compiled rules, please see the main [README.md](../../README.md).
