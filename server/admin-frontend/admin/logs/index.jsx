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
