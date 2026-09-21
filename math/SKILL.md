---
name: math
description: "Use Three.js math classes (Vector3, Euler, Quaternion, Matrix4, Spherical) correctly instead of hand-rolled trigonometry, including when to pick Euler vs Quaternion. Use when doing rotations, orbit positioning, or any vector/angle math in a Three.js game."
---

Prefer Three.js math classes (`Vector3`, `Euler`, `Quaternion`, `Matrix4`) over custom implementations: they are well-tested, handle edge cases, and integrate seamlessly with Three.js objects. The same goes for measurement primitives like `Box3` and coordinate helpers like `Spherical`. The throughline is the reference frame — world space versus local space — which is where even the built-ins mislead if you ignore it.

This document covers four areas. **Spherical Coordinates and Trigonometry** replaces manual `sin`/`cos`. **Rotations** covers choosing between `Euler` and `Quaternion`. **Billboards** covers camera-facing quads, which must be oriented in world space. **Measuring an object's size (Box3)** covers why measuring a skinned/animated character with `setFromObject` is corrupted, and what to do instead.

## Spherical Coordinates and Trigonometry

For spherical coordinates or anything involving `sin`/`cos`, use `Euler`, `Vector3`, and `Quaternion` rather than hand-rolled trigonometry. For an orbit position, build a `Spherical` and read it into a vector. For a direction from accumulated angles, build an `Euler` and apply it to a forward vector.

```typescript
// Instead of manual sin/cos for orbit position:
const spherical = new Spherical(radius, polarAngle, azimuthalAngle)
position.setFromSpherical(spherical)

// For direction from angles:
const euler = new Euler(pitch, yaw, 0, 'YXZ')
const direction = new Vector3(0, 0, -1).applyEuler(euler)
```

## Rotations

Rotations need careful handling, and the representation is chosen by use case. Use `Euler` with `'YXZ'` order for orbital and FPS cameras, where pitch and yaw accumulate separately. Use `Quaternion` for general rotations, for interpolation (`slerp`), and to avoid gimbal lock. When converting between representations, account for the `Euler` order. Staying in a single representation reduces bugs. Three.js objects expose both `.rotation` (an `Euler`) and `.quaternion` (a `Quaternion`), and keep them synced automatically.

## Billboards (labels, health bars, icons that face the camera)

A billboard quad must be oriented in **world** space. If it is a child of a rotating object (an enemy, a turret), copying the camera's orientation into its **local** rotation is wrong — the parent's world rotation still applies on top, so the quad tilts and spins with the parent. This local-rotation mistake is the usual cause of a health bar that is rotated incorrectly.

Fix A: orient in world space, compensating for the parent's world rotation. Fix B (simpler): do not parent the label to the moving object at all — keep it in world space and position it directly.

```typescript
// A — orient in world space, compensating for the parent's world rotation:
mesh.quaternion.copy(camera.quaternion) // desired WORLD rotation
const parentWorld = mesh.parent.getWorldQuaternion(new Quaternion())
mesh.quaternion.premultiply(parentWorld.invert()) // local = parentWorld⁻¹ · desiredWorld

// B (simpler) — don't parent it to the moving object; keep it in world space:
scene.add(label)
label.position.copy(targetWorldPosition).add(offset)
label.quaternion.copy(camera.quaternion)
```

`THREE.Sprite` always faces the camera automatically and avoids the problem entirely — prefer it for simple health bars and icons.

## Measuring an object's size (`Box3`) — beware skinned/rigged meshes

`new Box3().setFromObject(object)` is correct for **static** meshes. It is wrong and unstable for **skinned, rigged, or animated** objects such as characters, for two reasons. First, it unions every descendant — including the **skeleton bones** (which sit far outside the visible body) and any reference or clone sub-objects a character system keeps. Second, it expands to **bind-pose** geometry, so the box changes every frame as the animation poses the bones.

The wrong result is routinely 2–3× (or more) the visible body height, and it silently breaks anything sized from that number. The classic failure: scaling one character to match another's measured height produces a giant, because the measured character was live and animating (inflated) while the other was measured fresh (clean).

Use one of three correct options.

- Measure the **`SkinnedMesh`'s `geometry.boundingBox`** — the stable bind-pose mesh extent (`mesh.geometry.computeBoundingBox()`, then read `mesh.geometry.boundingBox`). Caveat: that box is in **local** geometry space; for a world-unit height, transform it by the mesh's world matrix — `mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld)` — which folds in scale from parent nodes, where a glTF's import scale usually lives. Reading it raw, or multiplying only by `mesh.scale`, measures a scaled character wrong.
- Measure the **raw model once on load**, before it is rigged, animated, or wrapped.
- Avoid measuring entirely: size against a **known constant** — a target character height you decide.

Don't `setFromObject` a live character every frame and trust the height.
