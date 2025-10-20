import React, { useState } from 'react';

const SeerVaultDiagram = () => {
  const [expandedLayer, setExpandedLayer] = useState(null);

  const securityLayers = [
    { id: 1, name: 'Cryptography', icon: '🔐', desc: 'Ed25519 & AES-256-GCM', bgColor: '#b91c1c', borderColor: '#dc2626' },
    { id: 2, name: 'Identity', icon: '👤', desc: 'Agent Registration & Credentials', bgColor: '#92400e', borderColor: '#d97706' },
    { id: 3, name: 'Authorization', icon: '⚖️', desc: 'Role-Based Access Control', bgColor: '#854d0e', borderColor: '#eab308' },
    { id: 4, name: 'Validation', icon: '✓', desc: 'Request Middleware', bgColor: '#4d7c0f', borderColor: '#84cc16' },
    { id: 5, name: 'Audit Logs', icon: '📋', desc: 'Comprehensive Logging', bgColor: '#15803d', borderColor: '#22c55e' },
    { id: 6, name: 'Rate Limiting', icon: '⏱️', desc: 'Abuse Prevention', bgColor: '#0e7490', borderColor: '#06b6d4' },
    { id: 7, name: 'TLS Encryption', icon: '🔒', desc: 'Secure Transport', bgColor: '#1e40af', borderColor: '#2563eb' },
    { id: 8, name: 'Analytics', icon: '📊', desc: 'Behavioral Detection', bgColor: '#6b21a8', borderColor: '#a855f7' },
    { id: 9, name: 'Async Workers', icon: '⚙️', desc: 'Background Processing', bgColor: '#3730a3', borderColor: '#6366f1' },
  ];

  const getLayerDetails = (id) => {
    const details = {
      1: "Uses Ed25519 for asymmetric encryption and AES-256-GCM for symmetric encryption",
      2: "Agents register once and receive cryptographic proof of identity",
      3: "Different operators have different access levels (supervisor vs staff)",
      4: "Every command validated before reaching control systems",
      5: "Regulatory compliance: every action recorded (who, what, when, why)",
      6: "Prevent brute force attacks and runaway commands",
      7: "Protect credentials and commands in transit",
      8: "Detect suspicious behavior patterns (e.g., 1000 commands in 10s)",
      9: "Keep system responsive while security checks run asynchronously",
    };
    return details[id] || "";
  };

  return (
    <div style={{ width: '100%', minHeight: '100vh', background: 'linear-gradient(to bottom right, #030712, #0f172a, #030712)', padding: '32px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <h1 style={{ fontSize: '48px', fontWeight: 'bold', background: 'linear-gradient(to right, #06b6d4, #60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '16px' }}>SeerSecure</h1>
          <p style={{ fontSize: '24px', fontWeight: '600', color: '#06b6d4', marginBottom: '8px' }}>Enabling Zero-Trust Autonomy in Industrial Agentic Systems</p>
          
        </div>

        {/* Main Architecture */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-block', background: 'linear-gradient(to right, #0369a1, #1e40af)', borderRadius: '8px', padding: '15px 30px', border: '2px solid #06b6d4' }}>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', margin: '0' }}>Problem Statement</p>
              <p style={{ color: '#cffafe', fontSize: '14px', marginTop: '4px', margin: '0' }}>
                    Modern industrial systems such as warehouses, factories, and energy plants are increasingly managed by autonomous software and AI agents that control sensors, 
                    actuators, and production processes. However, these Industrial Control Systems (ICS) were originally designed for
                    isolated environments and lack strong security boundaries. Once connected to corporate or cloud networks, they become
                    vulnerable to identity spoofing, lateral movement, and insider threats. 
              </p>
            </div>
          </div>
          
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-block', background: 'linear-gradient(to right, #072130ff, #b91c1c)', borderRadius: '8px', padding: '15px 30px', border: '2px solid #06b6d4' }}>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', margin: '0' }}>Challenge</p>
              <p style={{ color: '#cffafe', fontSize: '14px', marginTop: '4px', margin: '0' }}>
                    Despite its adoption in IT systems, zero-trust enforcement for autonomous agents remains an unsolved challenge due to lack of standardized agent
                    identification and authentication frameworks, absence of cryptographically enforced authorization in mult-agent ecosystems, limited integration of 
                    real-time behavioral analytics with AI driven reasoning and lastly the performance bottlecks when combining deep inspection, logging and cryptography
                    in live environments.
              </p>
            </div>
          </div>


          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-block', background: 'linear-gradient(to right, #0c3d57ff, #1d352dff  )', borderRadius: '8px', padding: '15px 30px', border: '2px solid #06b6d4' }}>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', margin: '0' }}>Research Question</p>
              <p style={{ color: '#cffafe', fontSize: '14px', marginTop: '4px', margin: '0' }}>
                   How can we design a high-performance, cryptographically verifiable, and behavior-aware security gateway that enforces zero-trust principles for autonomous 
                   industrial AI agents without compromising real-time responsiveness and operational efficiency?
              </p>
            </div>
          </div>

          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-block', background: 'linear-gradient(to right, #0c3d57ff, #059669    )', borderRadius: '8px', padding: '15px 30px', border: '2px solid #06b6d4' }}>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', margin: '0' }}>Our Solution</p> 
              <p style={{ color: 'black', fontSize: '12px', margin: '0' }}> A step towards Zero-Trust Agentic Framework (ZTAI)</p>
              <p style={{ color: '#cffafe', fontSize: '14px', marginTop: '4px', margin: '0' }}>
                   SeerSecure presents a Strands Zero-Trust  Security Wrapper which is a GoLang gateway that extends the Python-based Strands Agents SDK with nine integrated security layers.
                    These layers provide cryptographic identity proof, role-based authorization, request validation, audit logging, rate limiting, TLS encryption,
                    and asynchronous processing to ensure that every command from autonomous agents is verified and authorized before reaching industrial control systems like OpenPLC and ScadaBR.
                    By design, no agent request is ever trusted by default, every interaction is authenticated, authorized, validated, logged, and monitored before execution.
              </p>
            </div>
          </div>

          {/* Top: Warehouse Operators */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-block', background: 'linear-gradient(to right, #0369a1, #1e40af)', borderRadius: '8px', padding: '15px 30px', border: '2px solid #06b6d4' }}>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', margin: '0' }}>👥 Warehouse Operators & ScadaBR Dashboard</p>
              <p style={{ color: '#cffafe', fontSize: '14px', marginTop: '4px', margin: '0' }}>Requesting control & monitoring operations</p>
            </div>
          </div>

          {/* The Nine Security Layers - Concentric */}
          <div style={{ position: 'relative', margin: '0 auto', width: '100%', maxWidth: '600px', height: '384px', marginBottom: '48px' }}>
            {/* Outer circles */}
            {[0, 1, 2, 3, 4].map((ring) => (
              <div
                key={`ring-${ring}`}
                style={{
                  position: 'absolute',
                  border: '2px solid #4b5563',
                  borderRadius: '50%',
                  inset: `${ring * 15}%`,
                  opacity: 0.3
                }}
              />
            ))}

            {/* Center - Core System */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 20 }}>
              <div style={{ width: '96px', height: '96px', background: 'linear-gradient(to bottom right, #10b981, #059669)', borderRadius: '8px', border: '2px solid #34d399', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                  <p style={{ fontSize: '14px', fontWeight: 'bold', color: 'white', margin: '0' }}>OpenPLC &</p>
                  <p style={{ fontSize: '14px', fontWeight: 'bold', color: 'white', margin: '0' }}>ScadaBR</p>
                </div>
              </div>
            </div>

            {/* Security layers arranged in circle */}
            {securityLayers.map((layer, idx) => {
              const angle = (idx / securityLayers.length) * Math.PI * 2;
              const radius = 140;
              const x = Math.cos(angle) * radius;
              const y = Math.sin(angle) * radius;
              
              return (
                <div
                  key={layer.id}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                    zIndex: 10,
                    cursor: 'pointer'
                  }}
                  onClick={() => setExpandedLayer(expandedLayer === layer.id ? null : layer.id)}
                >
                  <div style={{
                    background: layer.bgColor,
                    borderRadius: '8px',
                    padding: '12px',
                    border: '2px solid white',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
                    width: '128px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.5)';
                    e.currentTarget.style.transform = 'scale(1.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.3)';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                  >
                    <p style={{ fontSize: '32px', margin: '0 0 8px 0' }}>{layer.icon}</p>
                    <p style={{ color: 'white', fontWeight: 'bold', fontSize: '12px', margin: '4px 0' }}>{layer.name}</p>
                    <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '11px', margin: '0', lineHeight: '1.3' }}>{layer.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* <div style={{ textAlign: 'center', color: '#9ca3af', fontSize: '14px', marginBottom: '48px' }}>
            💡 Click any security layer for details
          </div> */}

          {/* Expanded Layer Details */}
          {expandedLayer && (
            <div style={{ background: '#1e293b', border: '2px solid #06b6d4', borderRadius: '8px', padding: '24px', marginBottom: '48px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                <div>
                  <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#06b6d4', marginBottom: '12px', marginTop: 0 }}>{securityLayers[expandedLayer - 1].name}</h3>
                  <p style={{ color: '#cbd5e1', marginBottom: '12px' }}>{securityLayers[expandedLayer - 1].desc}</p>
                </div>
                <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px' }}>
                  <p style={{ fontSize: '14px', color: '#cbd5e1', margin: '0' }}>
                    {getLayerDetails(expandedLayer)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Data Flow Diagram */}
          <div style={{ background: '#1e293b', border: '2px solid #a855f7', borderRadius: '8px', padding: '32px', marginBottom: '48px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#d8b4fe', marginBottom: '24px', marginTop: 0 }}>Zero Trust Request Flow</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                { num: 1, title: 'Agent/Operator sends command', desc: 'Request enters the Go wrapper gateway' },
                { num: 2, title: 'Cryptographic verification', desc: 'Wrapper validates digital signature using Ed25519' },
                { num: 3, title: 'Role-based authorization', desc: 'Check if agent/operator has permission for this action' },
                { num: 4, title: 'Rate limit & anomaly check', desc: 'Detect abuse patterns and behavioral anomalies' },
                { num: 5, title: 'Execute & log', desc: 'Command reaches OpenPLC/ScadaBR, action logged for audit' },
              ].map((step) => (
                <div key={step.num} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '48px', height: '48px', background: 'linear-gradient(to bottom right, #06b6d4, #2563eb)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', flexShrink: 0 }}>
                    {step.num}
                  </div>
                  <div>
                    <p style={{ fontWeight: '600', color: 'white', margin: '0' }}>{step.title}</p>
                    <p style={{ fontSize: '14px', color: '#cbd5e1', margin: '4px 0 0 0' }}>{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Technologies */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '48px' }}>
            <div style={{ background: 'linear-gradient(to bottom right, #7f1d1d, #991b1b)', borderRadius: '8px', padding: '24px', borderLeft: '4px solid #fca5a5' }}>
              <p style={{ color: '#fecaca', fontSize: '14px', fontWeight: '600', marginBottom: '8px', margin: '0 0 8px 0' }}>🔐 Cryptography</p>
              <p style={{ color: 'white', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>Ed25519 & AES-256-GCM</p>
              <p style={{ color: '#cbd5e1', fontSize: '14px', margin: 0 }}>Military-grade encryption for identity proof and data confidentiality</p>
            </div>

            <div style={{ background: 'linear-gradient(to bottom right, #581c87, #7e22ce)', borderRadius: '8px', padding: '24px', borderLeft: '4px solid #d8b4fe' }}>
              <p style={{ color: '#d8b4fe', fontSize: '14px', fontWeight: '600', marginBottom: '8px', margin: '0 0 8px 0' }}>🤖 AI Analytics</p>
              <p style={{ color: 'white', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>AWS Bedrock Reasoning</p>
              <p style={{ color: '#cbd5e1', fontSize: '14px', margin: 0 }}>LLM-powered analysis for context-aware threat response</p>
            </div>

            <div style={{ background: 'linear-gradient(to bottom right, #1e3a8a, #1e40af)', borderRadius: '8px', padding: '24px', borderLeft: '4px solid #93c5fd' }}>
              <p style={{ color: '#93c5fd', fontSize: '14px', fontWeight: '600', marginBottom: '8px', margin: '0 0 8px 0' }}>📦 Deployment</p>
              <p style={{ color: 'white', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>Docker Compose</p>
              <p style={{ color: '#cbd5e1', fontSize: '14px', margin: 0 }}>Reproducible infrastructure with all components orchestrated</p>
            </div>
          </div>

          {/* System Components */}
          <div style={{ background: '#1e293b', border: '2px solid #06b6d4', borderRadius: '8px', padding: '32px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#06b6d4', marginBottom: '24px', marginTop: 0 }}>Complete System Architecture</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
              <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', borderLeft: '4px solid #06b6d4' }}>
                <p style={{ color: '#06b6d4', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>🛡️ Go Wrapper (Core Security)</p>
                <ul style={{ fontSize: '14px', color: '#cbd5e1', margin: '0', paddingLeft: '20px' }}>
                  <li>✓ HTTP REST API</li>
                  <li>✓ TLS certificates</li>
                  <li>✓ 9 integrated security layers</li>
                  <li>✓ Asynchronous verification</li>
                </ul>
              </div>

              <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', borderLeft: '4px solid #22c55e' }}>
                <p style={{ color: '#22c55e', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>🏭 SCADA Devices</p>
                <ul style={{ fontSize: '14px', color: '#cbd5e1', margin: '0', paddingLeft: '20px' }}>
                  <li>✓ OpenPLC (Industrial Controller)</li>
                  <li>✓ ScadaBR (Operator Dashboard)</li>
                  <li>✓ Physical equipment (conveyors, pumps, sensors)</li>
                </ul>
              </div>

              <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', borderLeft: '4px solid #a855f7' }}>
                <p style={{ color: '#a855f7', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>🐍 Python Integration</p>
                <ul style={{ fontSize: '14px', color: '#cbd5e1', margin: '0', paddingLeft: '20px' }}>
                  <li>✓ Strands Client SDK</li>
                  <li>✓ IDA Agent (Intelligent Detection)</li>
                  <li>✓ Multiple test agents</li>
                </ul>
              </div>

              <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', borderLeft: '4px solid #fbbf24' }}>
                <p style={{ color: '#fbbf24', fontWeight: 'bold', marginBottom: '8px', margin: '0 0 8px 0' }}>🔧 Infrastructure</p>
                <ul style={{ fontSize: '14px', color: '#cbd5e1', margin: '0', paddingLeft: '20px' }}>
                  <li>✓ Docker containerization</li>
                  <li>✓ pfSense firewall & network segmentation</li>
                  <li>✓ Audit logging & compliance</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SeerVaultDiagram;