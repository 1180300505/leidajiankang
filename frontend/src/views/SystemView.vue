<template>
  <section class="panel">
    <h2>System Config</h2>
    <p class="desc">Main interface for backend endpoint, thresholds, and user-level settings.</p>

    <div class="grid">
      <article class="card">
        <h3>Backend Connection</h3>
        <p>Placeholder for API base URL and socket status test.</p>
      </article>
      <article class="card">
        <h3>Threshold Management</h3>
        <p>Placeholder for alarm threshold and health score rules.</p>
      </article>
      <article class="card full">
        <h3>Access & Logs</h3>
        <p>Placeholder for role management and operation logs.</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.panel {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100vh - 40px);
  background:
    radial-gradient(circle at 20% 20%, rgba(61, 186, 255, 0.15), transparent 35%),
    linear-gradient(180deg, #051643, #082969 45%, #031a54);
  border: 2px solid #1dc5ff;
  border-radius: 14px;
  padding: 20px;
  color: #d9f5ff;
  box-shadow:
    inset 0 0 36px rgba(24, 124, 221, 0.22),
    0 0 22px rgba(21, 179, 255, 0.2);
}

.panel::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    linear-gradient(rgba(95, 181, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(95, 181, 255, 0.08) 1px, transparent 1px);
  background-size: 34px 34px;
}

h2 {
  margin: 0;
  font-size: 34px;
  color: #ecfaff;
  text-shadow: 0 0 12px rgba(121, 219, 255, 0.3);
}

.desc {
  color: #8fdfff;
  margin-top: 10px;
}

.grid {
  margin-top: 16px;
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.card {
  background: linear-gradient(180deg, rgba(10, 42, 106, 0.92), rgba(7, 28, 75, 0.92));
  border: 1px solid rgba(58, 197, 255, 0.48);
  border-radius: 10px;
  padding: 16px;
  box-shadow:
    inset 0 0 16px rgba(22, 164, 255, 0.14),
    0 0 12px rgba(26, 155, 255, 0.2);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  border-color: rgba(116, 231, 255, 0.75);
}

h3 {
  margin: 0 0 10px;
  color: #9fe9ff;
}

p {
  margin: 0;
  color: #d7f4ff;
  line-height: 1.6;
}

.full {
  grid-column: 1 / -1;
}
</style>
