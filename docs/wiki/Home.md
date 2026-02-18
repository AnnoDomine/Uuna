# 📚 Grand WoW Library Wiki

Welcome to the central documentation for the Library System. This system manages research, data mining, and knowledge synthesis for World of Warcraft data using a specialized multi-agent architecture.

## 🧭 Navigation

### 🏗️ Core Architecture

- [**System Flow**](architecture/SystemFlow.md) - Hub-and-Spoke model and Mermaid diagrams.
- [**Learning Logic**](architecture/LearningLogic.md) - How Cooperated Scoring and the "Bad Boy" Observer work.
- [**Training Phase**](architecture/TrainingPhase.md) - Human-in-the-loop and faked requests.
- [**Task Lifecycle**](architecture/SystemFlow.md#the-queue-concept) - The journey of a query.

### 👥 Agents & Roles

- [**The Librarian**](roles/Librarian.md) - The interface.
- [**The Courier**](roles/Courier.md) - The orchestrator.
- [**The Archivist**](roles/Archivist.md) - Database expert.
- [**The Expedition Group**](roles/ExpeditionGroup.md) - Online researchers.
- [**The Sentinel**](roles/Sentinel.md) - Security & Sanitization.
- [**The Sages**](roles/Sages.md) - Final quality control.
- [**The Tinker**](roles/Tinker.md) - Potential & Quantity judge.
- [**The Observer**](roles/Observer.md) - Reality & Quality judge.

### 📖 How to Use

- [**Requirements**](how-to-use/Requirements.md) - Hardware and software needs.
- [**Installation**](how-to-use/Installation.md) - Step-by-step setup.
- [**Data Acquisition**](how-to-use/DataAcquisition.md) - Getting data into the library.
- [**Getting Started**](how-to-use/GettingStarted.md) - First steps with the agents.

### 🛠️ Developer Notices

- [**Environment Specs**](developer-notices/DevSpecs.md) - Hardware used for dev and training.

### 💾 Data & Implementation

- [**Database Models**](data/DatabaseModels.md) - Schema for tasks, queues, and events.
- [**Vector Memory**](data/VectorMemory.md) - How agents remember patterns long-term.

---

_Maintained by the AI Orchestration Team._
