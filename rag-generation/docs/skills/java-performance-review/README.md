# 🚀 Java Performance Reviewer Skill

> **A knowledge base for AI agents that perform static performance reviews of Java Enterprise repositories.**

Detect real and potential performance bottlenecks, scalability risks, and architecture issues **before they reach production**.

---

## 🎯 Purpose

This project enables AI agents to identify real and potential performance issues before they reach production.

Unlike traditional linters, it focuses on **performance engineering** rather than coding style or formatting.

---

## 🛠 Supported Technologies

- ☕ Java
- 🌱 Spring Framework / Spring Boot
- 🗄 Hibernate / JPA
- ⚡ jOOQ
- 📝 SQL
- 🐘 PostgreSQL
- 🏛 Sybase
- 🔄 Liquibase
- 📨 Kafka
- 📬 ActiveMQ
- 🌐 REST
- 📖 OpenAPI
- 🔌 WebSocket
- ☸ Kubernetes
- ⚓ Helm

---

## 🔍 What the Skill Detects

- 🚨 SQL and Hibernate N+1 queries
- 📑 Missing or inefficient indexes
- ⏱ Long-running transactions
- 🔒 Lock contention
- 📦 Collection and Stream inefficiencies
- 🧠 JVM allocation hotspots
- 🚦 Blocking I/O
- 📨 Kafka producer/consumer bottlenecks
- 📊 Batch processing issues
- 🧵 Thread contention
- 📈 Scalability blockers
- 🏗 Distributed architecture bottlenecks
- 🔗 Microservice communication anti-patterns

---

## ✨ Features

- ✅ Evidence-based findings
- 🚦 Severity prioritization
- 🎯 Confidence level for every issue
- 🏗 Architecture analysis
- 📈 Scalability analysis
- 👀 Manual verification recommendations
- 📋 Executive summary generation
- 🌍 System-wide bottleneck detection
- 📄 HTML and Markdown report output

---

## 📁 Repository Structure

```text
SKILL.md                Entry point for AI agents
rules/                  Technology-specific performance rules
docs/                   Documentation and maintenance guides
prompts/                Example prompts
taxonomy/               Rule classification
```

---

## 🚀 Usage

Provide the target repository together with this Skill to your AI coding agent.

### 💬 Example Prompt

```text
Analyze this repository using this Skill and identify real and potential performance issues. Prioritize findings by severity and provide evidence-based recommendations.
```

---

## 📐 Design Principles

- 🧾 Evidence over assumptions
- 🚫 No false positives by design
- 🧩 Technology-specific expertise
- 🌍 System-level analysis
- 📚 Scalable knowledge base
- 🔧 Easy to extend

---

## 📌 Status

**🟢 MVP**

Designed to grow incrementally by adding new technologies and performance practices while maintaining a consistent rule structure.

---

⭐ **Contributions, improvements, and new performance rules are welcome!**