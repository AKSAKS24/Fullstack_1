# ABAP Agent Guidelines

* **Naming Conventions**: Use `Z` prefix for custom objects.  Variables should be prefixed according to their type (e.g., `lv_` for local variables, `lt_` for internal tables).
* **Modularization**: Break complex logic into FORM routines or methods.  Avoid monolithic programs.
* **Clarity**: Write self‑explanatory code with meaningful comments when appropriate.
* **Comments**: Use one asterisk `*` at column 1 for comments.  Comments should explain why, not what.