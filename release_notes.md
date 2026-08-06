# 🚀 AgentOS v1.0.0-rc1 - "The Agentic OS"

After extensive architecture design, code extraction, and native deployment, we are proud to announce the first release candidate of **AgentOS** – a complete, runnable Agentic Operating System built on Python, Kafka, and Claude-native definitions.

## ✨ What's New (Highlights)

- **11 Claude Agents**: Fully defined in `.claude/agents/` with native Markdown definitions.
- **Core Runtime (BL01-BL19)**: Event-driven microservices architecture (Audit, Policy, Permit, Recommendation, Intent Gateway, Governance Console).
- **Automatic Schema Compiler**: Reads Markdown agent definitions and automatically generates Kafka topics and JSON schemas (No manual config needed!).
- **Flexible UI Dashboard**: A dynamic SPA with two themes (Arzin & Pedramflow) and full i18n (English/Farsi) for human oversight.
- **Zero-Docker Native Deployment**: Fully runnable on Linux (WSL/Termux) using only `python3 -m` and native Kafka.

## 🛠️ How to Run Locally
1. Clone the repo.
2. Install deps: `sudo apt install python3-sqlalchemy` & `pip install --break-system-packages kafka-python pydantic fastapi uvicorn`.
3. Download Kafka 3.6.0 and extract to `~/kafka/`.
4. Run: `./scripts/fixed_deploy.sh`.
5. Open: `http://localhost:8089`.

## 📸 Preview
*(Add a screenshot of your running dashboard at `http://localhost:8089`)*

## 📂 Architecture Layer Breakdown
- **Layer 1:** `.claude/agents`, `governance/`, `workflows/`.
- **Layer 2:** `src/core_services`, `src/domain_services`, `src/governance_console`.
- **Layer 3:** `ui/`.

---

**Next Steps:**
- Integration of real Claude API responses into the Agent Bridge.
- End-to-end testing of the full decision flow (Human-Agent-Human).
- Containerization for cloud deployment.
