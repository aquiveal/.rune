---
name: data-architecture
description: A machine-readable operational guide for navigating and applying the authoritative architectural rules stored within this repository.
---
# Architectural & Information Engineering Library

This skill serves as the machine-readable operational guide for navigating and applying the authoritative architectural rules stored within this repository. Use this skill to transform raw technical requirements into structurally sound, industry-standard information systems.

## 1. Define Clear Boundaries

### Scope
- **Domain:** Information Architecture (IA), Data Modeling, Content Strategy, Taxonomy Design, and Database Reliability Engineering.
- **Workflow:** System design, metadata schema creation, navigation planning, and ecosystem mapping.
- **Permission Level:** Read-only access to the rulebook library; operational execution in the project workspace.

### Usage Trigger
This skill MUST be activated whenever the AI is tasked with:
- Designing a new database or content schema.
- Creating or auditing a taxonomy or controlled vocabulary.
- Planning user journeys across multiple channels (web, mobile, IoT).
- Restructuring legacy information systems.
- Defining enterprise-level content governance.

## 2. Structural Overview

### Mental Map
The system is organized as a hierarchical library of "Operational Rulebooks" derived from authoritative literature.
1.  **Repository Root:** The entry point for library traversal.
2.  **Book Directories:** Grouped by foundational text (e.g., `information-architecture-fourth-edition...`).
3.  **Chapter Rulebooks:** Individual `.md` files containing domain-specific `@Tags` for AI ingestion.

### Key Components
| Component | Description |
| :--- | :--- |
| **`@Domain`** | Specifies when the rulebook MUST be triggered. |
| **`@Vocabulary`** | Defines the mandatory mental model and terminology. |
| **`@Objectives`** | States the required outcomes for the task. |
| **`@Guidelines`** | Detailed constraints and design rules. |
| **`@Workflow`** | Step-by-step algorithmic process for execution. |
| **`@Examples`** | Concrete Do's and Don'ts for pattern matching. |

## 3. Documented Workflows

### Workflow: Executing an Architectural Task
1.  **Contextual Triage:** Analyze the user request to identify the primary problem domain (e.g., "I need a way to organize my company's documents").
2.  **Library Selection:** Use the **Decision Matrix** (Section 4) to identify the relevant directory.
3.  **Rulebook Ingestion:** Read the `.md` file corresponding to the specific sub-task (e.g., `01-what-are-taxonomies.md`).
4.  **Constraint Extraction:** Parse the `@Guidelines` and `@Objectives` to establish boundaries.
5.  **Step-wise Execution:** Follow the `@Workflow` section within the selected rulebook.
6.  **Validation:** Perform a "Do's and Don'ts" check against the `@Examples` before finalizing the output.

## 4. Simple "If/Then" Decision Rules

### Selection Matrix
| If the task involves... | Then use directory... |
| :--- | :--- |
| Taxonomies, Synonyms, Thesauri | `accidental-taxonomist-second-edition...` |
| Navigation, Labeling, Search UX | `information-architecture-fourth-edition...` |
| Multi-channel Content, Content APIs | `content-everywhere-sara-wachter-boettcher` |
| Distributed Systems, Scalability | `designing-data-intensive-applications...` |
| Universal Data Entities (People/Products) | `data-model-resource-book-volume-one...` |
| Industry Verticals (Health/Insurance) | `data-model-resource-book-revised-edition...` |
| Database Ops, Reliability, SRE | `database-reliability-engineering...` |
| Content Governance, Enterprise Ops | `enterprise-content-strategy-kevin-nichols` |
| Initial Research, Card Sorting | `card-sorting-donna-spencer` |
| General "Information Messes" | `how-to-make-sense-of-any-mess-abby-covert` |

### Selection Logic
- **If** multiple domains overlap, **then** prioritize the most specific rulebook first (e.g., use `accidental-taxonomist` for the taxonomy part and `information-architecture` for the navigation part).
- **If** the task is a high-level strategy, **then** start with `how-to-make-sense-of-any-mess` or `information-architecture`.

## 5. Guardrails and Common Pitfalls

### Negative Constraints
- **DO NOT** use generic LLM training data for architectural definitions when a specific rule exists in this library.
- **DO NOT** mix hierarchical and associative relationships unless explicitly permitted by the `@Guidelines` in the selected rulebook.
- **DO NOT** skip the "Scale Verification Check" (Cathedral vs. Garage) defined in the IA rulebooks.
- **DO NOT** hardcode device-specific presentation logic into foundational data models.

### Known Failure Modes
- **Term Ambiguity:** If a term has multiple meanings, you MUST add a `Scope Note` as per the `accidental-taxonomist` workflow.
- **Polyhierarchy Conflict:** Ensure the system supports multiple parents before assigning them.
- **Contextual Proliferation:** Failing to decouple content from containers leads to "locked" data.

## 6. Syntax & Configuration References

### Header Syntax (@Tags)
Rulebooks utilize the following custom headers for semantic parsing:
- `# @Domain`: Regex/String triggers for activation.
- `# @Vocabulary`: Dictionary of required terms.
- `# @Objectives`: Success criteria.
- `# @Guidelines`: Rules and constraints.
- `# @Workflow`: Ordered execution steps.
- `# @Examples (Do's and Don'ts)`: Pattern-based validation.

### Formatting Requirements
- All data models generated SHOULD be in `JSON` or `YAML` unless specified.
- Taxonomy exports SHOULD favor `SKOS` (XML/RDF) for machine readability.
- Diagrams SHOULD be rendered in `Mermaid` syntax.
