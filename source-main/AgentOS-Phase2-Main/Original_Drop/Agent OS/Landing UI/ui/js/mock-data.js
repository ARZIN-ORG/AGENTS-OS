export const MOCK = {
  system:{
    name:"Arzin Agent OS — Governance Console",
    phase:"Phase-1 (Human-in-the-loop, Suggestion-only)",
    build:"UI Prototype v1.0",
    lastSync:""+new Date().toISOString()
  },
  channels:[
    {id:"aacp.core", mode:"parallel", sla:"p99<120ms", status:"ok"},
    {id:"aacp.audit", mode:"parallel", sla:"p99<250ms", status:"ok"},
    {id:"aacp.partner.shadow", mode:"parallel", sla:"p99<200ms", status:"warn"},
  ],
  agents:[
    {layer:"OS-Native", name:"Governance Agent", code:"BL19", status:"ok", owner:"Governance"},
    {layer:"OS-Native", name:"Policy Plane Agent", code:"BL07", status:"ok", owner:"Gov/Policy"},
    {layer:"OS-Native", name:"Permit / Authorization Agent", code:"BL08", status:"ok", owner:"Permit"},
    {layer:"OS-Native", name:"Audit & Trace Agent", code:"BL01/BL08", status:"ok", owner:"Audit"},
    {layer:"OS-Native", name:"Channel Manager Agent", code:"BL05", status:"ok", owner:"Platform"},
    {layer:"OS-Native", name:"Registry & Identity Agent", code:"BL06", status:"ok", owner:"Platform"},
    {layer:"OS-Native", name:"Signature & Trust Agent", code:"BL03", status:"warn", owner:"Security"},
    {layer:"Infrastructure", name:"Infrastructure Health Advisor", code:"INF-01", status:"ok", owner:"Ops"},
    {layer:"Infrastructure", name:"Capacity & Cost Optimization Agent", code:"INF-02", status:"ok", owner:"FinOps"},
    {layer:"Infrastructure", name:"Security Posture Advisor", code:"INF-03", status:"warn", owner:"SecOps"},
    {layer:"Domain", name:"Operational Planning Advisor", code:"DOM-01", status:"ok", owner:"Ops"},
    {layer:"Domain", name:"Performance Variance Analyzer", code:"DOM-02", status:"ok", owner:"Ops/Data"},
    {layer:"Domain", name:"Forecast & Trend Advisor", code:"DOM-03", status:"warn", owner:"Planning"},
    {layer:"Interaction", name:"Intent Interpretation Agent", code:"BL17", status:"ok", owner:"Interaction"},
    {layer:"Interaction", name:"Explanation & Justification Agent", code:"INT-02", status:"ok", owner:"Interaction"},
    {layer:"Interaction", name:"Executive Narrative Agent", code:"INT-03", status:"ok", owner:"Interaction"}
  ],
  policies:[
    {id:"POL-001", name:"No Direct Execution", version:"1.0.0", status:"active"},
    {id:"POL-002", name:"MFA → Intent → Confirm → Permit → Publish", version:"1.0.0", status:"active"},
    {id:"POL-003", name:"Reject-on-Missing Audit Envelope", version:"1.0.0", status:"active"},
  ],
  permits:[
    {id:"PRM-7712", subject:"op:scale:kafka", status:"pending", requestedBy:"CTO", risk:"medium"},
    {id:"PRM-7728", subject:"op:rotate:cert", status:"approved", requestedBy:"Gov", risk:"low"},
    {id:"PRM-7730", subject:"partner:onboard:shadow", status:"rejected", requestedBy:"Gov", risk:"high"},
  ],
  audit:[
    {ts:"2026-01-07T10:22:13Z", trace:"tr_9f1", event:"PERMIT_APPROVED", actor:"gov:board", channel:"aacp.core"},
    {ts:"2026-01-07T10:22:14Z", trace:"tr_9f1", event:"PUBLISH_ALLOWED", actor:"permit", channel:"aacp.core"},
    {ts:"2026-01-07T10:24:01Z", trace:"tr_aa2", event:"MESSAGE_REJECTED", actor:"interceptor", channel:"aacp.core"},
  ]
};
