#!/bin/bash
set -e
echo "🚀 STARTING IMPLEMENTATION..."

# Kill previous processes to free ports
echo "🔄 Freeing ports 8080, 8081, 8082, 8083, 8090..."
fuser -k 8080/tcp 2>/dev/null || true
fuser -k 8081/tcp 2>/dev/null || true
fuser -k 8082/tcp 2>/dev/null || true
fuser -k 8083/tcp 2>/dev/null || true
fuser -k 8090/tcp 2>/dev/null || true
sleep 2

export KAFKA_BROKER="localhost:9092"
export PYTHONPATH="$PYTHONPATH:$(pwd)"
export AUTH_ENABLED=false

# 1. Start Kafka & Zookeeper in background
cd ~/kafka/kafka_2.13-3.4.0
bin/zookeeper-server-start.sh config/zookeeper.properties > /dev/null 2>&1 &
sleep 5
bin/kafka-server-start.sh config/server.properties > /dev/null 2>&1 &
sleep 10

# 2. Start core services
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS
python3 -m src.core_services.agent_registry_service.main &
echo "✅ Agent Registry (port 8080)"
sleep 2

python3 -m src.core_services.bl07_policy_plane_service_v1.policy_plane_service.main &
echo "✅ Policy Plane (port 8081)"
sleep 2

python3 -m src.core_services.bl08_permit_service_v1.permit_service.main &
echo "✅ Permit Service (port 8082)"
sleep 2

python3 -m src.core_services.audit_sink.main &
echo "✅ Audit Sink (port 8083)"
sleep 2

# 3. Governance Console
AUTH_ENABLED=false python3 -m src.governance_console.bl19_governance_console_service_v2_sso_rbac_np.app.main &
echo "✅ Governance Console (port 8090)"
sleep 3

# 4. Run compiler
cd src/infrastructure/agent_schema_compiler && python3 compiler.py
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS

# 5. Start UI (using the correct 'ui' folder)
cd ui && python3 -m http.server 8089 &
echo "✅ UI at http://localhost:8089"

echo "====================================================================="
echo "🌐 All services are UP and OK."
echo "📊 Dashboard: http://localhost:8089"
echo "🔍 For testing: ps aux | grep python"
echo "====================================================================="
