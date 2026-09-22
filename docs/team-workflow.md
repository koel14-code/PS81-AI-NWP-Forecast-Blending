# Team Development & Git Workflow Guidelines

## GitHub Collaboration Rules

To ensure smooth multi-developer collaboration during SIH:

### 1. Branch Naming Conventions
- `main`: Production-ready releases only.
- `dev`: Default integration branch.
- `feature/<name>`: New feature implementations (e.g., `feature/xarray-ingestion`, `feature/quantile-blender`).
- `fix/<issue>`: Bug fixes (e.g., `fix/grib-loader-windows`).

### 2. Commit Message Standard
Use structured commit messages:
- `feat: add GFS gridded parser in src/data/`
- `fix: resolve bounding box lat/lon slice ordering`
- `docs: update methodology equations in docs/methodology.md`

### 3. Pull Request (PR) Checklist
Before submitting a PR to `dev`:
1. Ensure your code conforms to standard PEP8 styling.
2. Run pytest to confirm all existing tests pass:
   ```bash
   pytest
   ```
3. Avoid committing raw dataset files (`.nc`, `.grib2`, `.csv`) or local virtual environments.

### 4. Code Ownership & Subpackages
- **Data Ingestion**: `src/data/`
- **Feature Extraction**: `src/features/`
- **Blending Logic**: `src/blending/` & `src/models/`
- **Evaluation**: `src/evaluation/`
- **Dashboard UI**: `dashboard/`
