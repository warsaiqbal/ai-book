---
id: 1
title: Create Course Constitution
stage: constitution
date_iso: 2025-12-11
surface: agent
model: Qwen
feature: none
branch: main
user: qwen_user
command: /sp.constitution
labels:
  - constitution
  - physical-ai
  - humanoid-robotics
  - course
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml: []
---

# Create Course Constitution

## User Input

```
/sp.constitution # Book Constitution — Physical AI & Humanoid Robotics

## Source of Truth
All content must follow the official course document *Hackathon I: Physical AI & Humanoid Robotics Textbook* exactly (structure, outcomes, weekly schedule, modules, hardware, labs, capstone).

## Purpose
Generate a Docusaurus-based, AI-native textbook mirroring the official document.  
Include clear explanations, minimal but effective code snippets, and tooling instructions.

## Required Sections (in order)
1. Introduction & Course Overview  
2. Module 1 — The Robotic Nervous System (ROS2)  
3. Module 2 — The Digital Twin (Gazebo & Unity)  
4. Module 3 — The AI-Robot Brain (NVIDIA Isaac)  
5. Module 4 — Vision-Language-Action (VLA)  
6. Weekly Breakdown (Weeks 1–13)  
7. Assessments & Capstone (voice → plan → navigate → identify → manipulate)  
8. Hardware Requirements (Digital Twin workstation, Jetson kits)  
9. Robot Lab Options (Proxy, Mini Humanoid, Premium)  
10. Cloud vs On-Prem Notes (latency, sim-to-real)  
11. Deployment & Integrations (RAG chatbot, Spec-Kit, agents)  
12. Appendix (examples, commands)

## Fidelity Rules
- Preserve structure, topics, learning outcomes, weekly items, and hardware specs.  
- Recreate tables and numbers exactly.  
- Paraphrase only for clarity, never change meaning.

## RAG Chatbot Requirements
- Use Qdrant + Neon Postgres + FastAPI.  
- Support "answer from highlighted text only."  
- Include architecture, setup steps, and minimal API code examples.

## Tools Integration
- Provide Spec-Kit Plus + Agent examples for chapter generation and assessments.  
- Include optional Better-Auth signup → personalized examples.

## Frontmatter Template
```yaml
---
title: "<Chapter Title>"
description: "<1 sentence>"
sidebar_position: <int>
learning_outcomes:
  - "Outcome"
tags: ["ros2","isaac","gazebo","vla"]
source_of_truth: "Official course document"
---
```
```

## Response Summary

Updated the project constitution to create a specific constitution for the Physical AI & Humanoid Robotics Course. The new constitution includes 6 core principles that align with the course requirements:

1. Source of Truth Fidelity
2. Multi-Platform Documentation
3. Structured Content Delivery
4. Preservation of Official Information
5. Integrated AI Tools
6. Advanced RAG Implementation

The constitution also defines Technology Stack Requirements, Development Workflow, and Governance sections relevant to the course objectives. A version 1.0.0 was created with today's date as the ratification date.