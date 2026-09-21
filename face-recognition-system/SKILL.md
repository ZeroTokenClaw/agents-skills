---
name: face-recognition-system
description: Implements secure and accurate facial recognition workflows including embedding comparison, validation, and check-in logic.
---

# Face Recognition System

## Instructions

1. Capture face image
2. Generate embedding
3. Compare with stored embeddings
4. Calculate similarity score
5. Apply threshold validation
6. Validate event context
7. Register check-in

## Constraints

- Must respect EventAIConfig
- Must prevent duplicate check-ins
- Must validate active event

## Security

- Never trust client-side matching
- Always validate on server
- Protect embeddings

## Performance

- Limit number of comparisons
- Use indexed embeddings if possible

## Anti-Patterns

- Accepting low confidence matches
- Matching outside event scope
- Ignoring multiple faces

## Example

Face detected → embedding → match → confidence 0.82 → approved.
