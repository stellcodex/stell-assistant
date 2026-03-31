# STELL Assistant

User-facing interaction layer for STELLCODEX.

## Role in System

STELL Assistant is the interface surface that connects users to the STELLCODEX ecosystem.

It is responsible for:
- user interaction
- assistant workflows
- guided system access
- decision execution surfaces
- communication-oriented control paths

## System Position

Within the STELLCODEX architecture:

- **STELLCODEX** → product and workflow surface
- **STELL-AI** → intelligence and decision authority
- **ORCHESTRA** → execution and state authority
- **STELL Assistant** → user-facing assistant interaction layer

## Purpose

This repository exists to provide a clean assistant surface for interacting with STELLCODEX capabilities without collapsing system boundaries.

It does not replace:
- STELL-AI intelligence authority
- ORCHESTRA execution authority
- core infrastructure ownership

## Repository Notes

- keep this repo focused on interaction surfaces
- avoid moving intelligence logic here
- avoid moving workflow/state authority here
- preserve architectural boundaries

## Related Repositories

- Main platform: `stellcodex/stellcodex`
- Intelligence layer: `stellcodex/stell-ai`
- Execution layer: `stellcodex/orchestra`
- Infrastructure layer: `stellcodex/infra`
