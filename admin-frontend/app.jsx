const { useState, useEffect } = React;

const API_BASE = '';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = options.headers ? { ...options.headers } : {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (!res.ok) throw new Error('API error');
  return res.json();
}

function Dashboard() {
  const [devices, setDevices] = useState([]);
  useEffect(() => {
    apiFetch('/devices').then(setDevices).catch(console.error);
  }, []);
  const total = devices.length;
  const modelCounts = devices.reduce((acc, d) => {
    const m = d.model || 'Desconocido';
    acc[m] = (acc[m] || 0) + 1;
    return acc;
  }, {});
  const alerts = [];
  devices.forEach(d => {
    const s = d.status || {};
    if (s.battery && s.battery < 20) alerts.push(`Batería baja en ${d.deviceId} (${s.battery}%)`);
    if (s.rootAttempt) alerts.push(`Intento de root en ${d.deviceId}`);
  });
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Dispositivos registrados: {total}</p>
      <h3>Distribución por modelo</h3>
      <ul>
        {Object.entries(modelCounts).map(([m, c]) => (
          <li key={m}>{m}: {c}</li>
        ))}
      </ul>
      <h3>Alertas</h3>
      <ul>
        {alerts.length ? alerts.map((a, i) => <li key={i}>{a}</li>) : <li>Sin alertas</li>}
      </ul>
    </div>
  );
}

function DeviceTable({ onSelect }) {
  const [devices, setDevices] = useState([]);
  const [search, setSearch] = useState('');
  useEffect(() => {
    apiFetch('/devices').then(setDevices).catch(console.error);
  }, []);
  const filtered = devices.filter(d =>
    [d.deviceId, d.imei, d.model, d.serial]
      .filter(Boolean)
      .some(v => v.toLowerCase().includes(search.toLowerCase()))
  );
  return (
    <div>
      <h2>Dispositivos</h2>
      <input placeholder="Buscar..." value={search} onChange={e => setSearch(e.target.value)} />
      <table>
        <thead>
          <tr>
            <th>IMEI</th>
            <th>Modelo</th>
            <th>Serial</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(d => (
            <tr key={d.deviceId} onClick={() => onSelect(d.deviceId)} style={{ cursor: 'pointer' }}>
              <td>{d.imei}</td>
              <td>{d.model}</td>
              <td>{d.serial}</td>
              <td>{d.status?.battery ? `Bat ${d.status.battery}%` : ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DeviceLogs({ id }) {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    apiFetch(`/logs/${id}`).then(d => setLogs(d.logs || [])).catch(console.error);
  }, [id]);
  if (!logs.length) return <p>Sin registros</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Tipo</th>
          <th>Severidad</th>
          <th>Mensaje</th>
        </tr>
      </thead>
      <tbody>
        {logs.map((l, i) => (
          <tr key={i}>
            <td>{new Date((l.timestamp || 0) * 1000).toLocaleString()}</td>
            <td>{l.type}</td>
            <td>{l.severity}</td>
            <td>{l.message}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function DeviceDetails({ id, onBack }) {
  const [info, setInfo] = useState(null);
  useEffect(() => {
    apiFetch(`/devices/${id}`).then(setInfo).catch(console.error);
  }, [id]);
  const sendCommand = async (action) => {
    try {
      await apiFetch(`/api/device/${action}`, {
        method: 'POST',
        body: JSON.stringify({ deviceId: id })
      });
      alert('Comando enviado');
    } catch (e) {
      alert('Error enviando comando');
    }
  };
  return (
    <div>
      <h2>Dispositivo {id}</h2>
      {info && (
        <div>
          <p>Modelo: {info.model}</p>
          <p>Serial: {info.serial}</p>
          <p>IMEI: {info.imei}</p>
          <p>Batería: {info.status?.battery ?? 'N/A'}%</p>
        </div>
      )}
      <div className="actions">
        <button onClick={() => sendCommand('wipe')}>Borrar Datos</button>
        <button onClick={() => sendCommand('reboot')}>Reiniciar</button>
        <button onClick={() => sendCommand('lock')}>Bloquear</button>
        <button onClick={() => sendCommand('screenshot')}>Tomar Captura</button>
      </div>
      <h3>Historial de Logs</h3>
      <DeviceLogs id={id} />
      <button onClick={onBack}>Volver</button>
    </div>
  );
}

function PolicyEditor() {
  const [name, setName] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Política "${name}" creada (demo)`);
    setName('');
  };
  return (
    <div>
      <h2>Editor de Políticas</h2>
      <form onSubmit={handleSubmit}>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Nombre" />
        <button type="submit">Guardar</button>
      </form>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.hash || '#/dashboard');
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash || '#/dashboard');
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleTokenChange = (e) => {
    const v = e.target.value;
    setToken(v);
    localStorage.setItem('token', v);
  };

  let page;
  if (route === '#/dashboard') page = <Dashboard />;
  else if (route === '#/devices') page = <DeviceTable onSelect={(id) => window.location.hash = `#/devices/${id}`} />;
  else if (route.startsWith('#/devices/')) {
    const id = route.split('/')[2];
    page = <DeviceDetails id={id} onBack={() => window.location.hash = '#/devices'} />;
  } else if (route === '#/policies') page = <PolicyEditor />;
  else page = <Dashboard />;

  return (
    <div>
      <header>
        <h1>Bizon MDM Admin</h1>
        <nav>
          <a href="#/dashboard">Dashboard</a>
          <a href="#/devices">Dispositivos</a>
          <a href="#/policies">Políticas</a>
        </nav>
        <input value={token} onChange={handleTokenChange} placeholder="JWT token" style={{ marginLeft: '1rem' }} />
      </header>
      <main style={{ padding: '1rem' }}>
        {page}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
