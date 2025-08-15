const { useState, useEffect } = React;

function AuditLogs() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    // Placeholder: backend not yet providing system logs; avoid breaking the UI
    setItems([]);
  }, []);
  return (
    <div>
      <h2>Logs de auditoría</h2>
      {items.length === 0 ? <p className="muted">Sin registros</p> : (
        <ul>{items.map((x,i) => <li key={i}>{JSON.stringify(x)}</li>)}</ul>
      )}
    </div>
  );
}

window.AuditLogs = AuditLogs;
const { useState, useEffect } = React;

function AuditLogs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (window.apiFetch) {
      window.apiFetch('/api/logs')
        .then(d => setLogs(d.logs || []))
        .catch(() => setLogs([]));
    }
  }, []);

  return (
    <div>
      <h2>Auditoría</h2>
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Acción</th>
            <th>Usuario</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l, i) => (
            <tr key={i}>
              <td>{l.date || '-'}</td>
              <td>{l.action}</td>
              <td>{l.user || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

window.AuditLogs = AuditLogs;
