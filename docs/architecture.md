# Project Ember Architecture

## Overview

Project Ember uses a modular local-first architecture designed around real-time conversational interaction.

The system combines local LLM inference, speech processing, behavioral filtering, and OBS integration into a unified interaction pipeline.

---

# High-Level Flow

Microphone Input
↓
Voice Activity Detection (VAD)
↓
Speech-to-Text (Faster-Whisper)
↓
Mistral 7B via Ollama
↓
Behavior / Context Layer
↓
Text-to-Speech (Piper)
↓
OBS Avatar + Audio Output

---

# Core Modules

## STT (Speech-to-Text)

Handles:

* microphone input
* transcription
* speech segmentation

## LLM Core

Handles:

* prompt orchestration
* conversational processing
* response generation

## Behavior Layer

Handles:

* response cleanup
* contextual tuning
* reactive behavior logic

## TTS (Text-to-Speech)

Handles:

* voice synthesis
* audio generation
* playback delivery

## OBS Integration

Handles:

* avatar state switching
* talking/idle animation
* stream interaction systems
