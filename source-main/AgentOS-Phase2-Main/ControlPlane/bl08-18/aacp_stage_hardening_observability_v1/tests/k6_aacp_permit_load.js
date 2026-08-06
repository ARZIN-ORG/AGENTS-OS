/// k6 load test for Permit Service (Phase-1)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '60s',
};

const base = __ENV.PERMIT_URL || 'http://permit-service:8082';

export default function () {
  const payload = JSON.stringify({
    trace_id: 't-' + __VU + '-' + __ITER,
    message_id: 'm-' + __VU + '-' + __ITER,
    channel_id: 'ch-default',
    topic: 'PAYMENT_INITIATED',
    agent_id: 'agent-test',
    agent_class: 'ExecutionAgent',
    envelope_hash: 'deadbeef',
    chain_hash: 'beadfeed'
  });

  const res = http.post(base + '/v1/permit/check', payload, { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'status is 200/403/409': (r) => [200,403,409].includes(r.status) });
  sleep(0.1);
}
