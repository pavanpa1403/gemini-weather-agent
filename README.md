#  Gemini Weather Agent

A Gemini-powered Agentic AI application that uses an external weather API as a tool to retrieve real-time weather information and then uses Gemini for reasoning, comparison, scoring, and travel recommendations.

---

##  Project Overview

This project demonstrates how an LLM can work with external tools.

Instead of relying only on the knowledge stored inside the LLM, Gemini can request an external weather tool whenever current weather information is required.

The application can:

- Get current weather information
- Handle multiple cities
- Compare weather conditions
- Score cities for travel
- Rank cities
- Select the best city
- Provide clothing recommendations
- Provide umbrella recommendations
- Handle weather API errors

---

##  Architecture

```text
                    USER
                      │
                      ▼
                 GEMINI LLM
                (Reasoning)
                      │
                      ▼
               Tool Decision
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Hyderabad    Chennai      Mumbai
          │           │           │
          └───────────┼───────────┘
                      ▼
               Weather Tool
                      │
                      ▼
                 wttr.in API
                      │
                      ▼
                Weather Data
                      │
                      ▼
                 GEMINI LLM
                      │
                  Analysis
                      │
                      ▼
                 Scoring
                      │
                      ▼
              Decision Making
                      │
                      ▼
             Final Recommendation