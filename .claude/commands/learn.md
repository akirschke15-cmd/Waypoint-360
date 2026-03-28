---
name: learn
description: Generate documentation and learning resources for code, architecture, or patterns
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Learn Command

Route to the **Technical Writer** agent to generate documentation, learning resources, and knowledge sharing materials.

## Usage

```
/learn <topic_or_module>
```

## Examples

### Example 1: Module Documentation
```
/learn auth module implementation and patterns
```

Response: Technical Writer:
1. Generates architecture overview
2. Creates API documentation
3. Provides usage examples
4. Lists common patterns and anti-patterns
5. Includes troubleshooting guide

### Example 2: Pattern Learning
```
/learn React hooks best practices
```

Response: Technical Writer:
1. Explains hook lifecycle
2. Shows correct usage patterns
3. Demonstrates common mistakes
4. Provides real code examples
5. Links to advanced resources

### Example 3: System Architecture
```
/learn how the payment system works
```

Response: Technical Writer:
1. Creates architecture diagram
2. Documents data flow
3. Lists key components
4. Explains integration points
5. Provides sequence diagrams

## Documentation Types

- **API Documentation**
  - Endpoint descriptions
  - Request/response formats
  - Authentication requirements
  - Error handling
  - Code examples

- **Architecture Guides**
  - System design
  - Component relationships
  - Data flow diagrams
  - Deployment model
  - Scaling considerations

- **Getting Started**
  - Setup instructions
  - First feature implementation
  - Common tasks walkthrough
  - Troubleshooting guide

- **Best Practices**
  - Patterns and anti-patterns
  - Do's and don'ts
  - Performance considerations
  - Security guidelines

- **Troubleshooting**
  - Common issues and solutions
  - Debug strategies
  - Where to look for problems
  - How to report issues

## Content Quality Standards

- **Clarity**: Written for target audience level
- **Accuracy**: Code examples tested
- **Completeness**: Covers common use cases
- **Currency**: Up-to-date with latest code
- **Accessibility**: Easy to scan and search

## Output Formats

- **Markdown**: README, API docs, guides
- **Diagrams**: Architecture, flow, sequence
- **Code Examples**: Commented, copy-paste ready
- **Videos**: Screen recording, narration (optional)
- **Interactive**: Runnable examples, sandboxes

## When to Use

- Documenting new features
- Creating onboarding materials
- Building knowledge base
- Explaining complex systems
- Team training and education

## When NOT to Use

- Code implementation (use other commands)
- Quick fix documentation (inline comments)
- External marketing content
- User-facing product docs (handled by product)
