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
// Expose helper for other modules
window.apiFetch = apiFetch;

function ServerStatus() {
  const [status, setStatus] = useState(null);
  useEffect(() => {
    const fetchStatus = () => apiFetch('/api/status').then(setStatus).catch(() => setStatus({}));
    fetchStatus();
    const id = setInterval(fetchStatus, 10000);
    return () => clearInterval(id);
  }, []);
  const ok = status && status.database && status.firebase;
  const color = ok ? 'green' : 'red';
  return (
    <span
      title={`DB:${status?.database ? 'ok' : 'fail'} Firebase:${status?.firebase ? 'ok' : 'fail'}`}
      style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: color, marginLeft: '0.5rem' }}
    />
  );
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
    if (s.wipeDetected) alerts.push(`Wipe detectado en ${d.deviceId}`);
    if (s.bootloaderTampered) alerts.push(`Bootloader modificado en ${d.deviceId}`);
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

function FirebaseConfigForm() {
  const [key, setKey] = useState('');
  const [message, setMessage] = useState('');
  useEffect(() => {
    apiFetch('/api/config/fcm').then(d => setKey(d.key || '')).catch(console.error);
  }, []);
  const save = () => {
    apiFetch('/api/config/fcm', { method: 'POST', body: JSON.stringify({ key }) })
      .then(() => setMessage('Clave de Firebase guardada correctamente'))
      .catch(() => setMessage('Error al guardar la clave'));
  };
  const test = () => {
    apiFetch('/api/test-fcm', { method: 'POST' })
      .then(r => setMessage(`Notificación enviada a ${r.sent} dispositivos`))
      .catch(() => setMessage('Error al conectar con Firebase'));
  };
  return (
    <div>
      <input value={key} onChange={e => setKey(e.target.value)} placeholder="FCM Server Key" />
      <div>
        <button onClick={save}>Guardar</button>
        <button onClick={test}>Probar conexión</button>
      </div>
      {message && <p>{message}</p>}
    </div>
  );
}

function Config() {
  return (
    <div>
      <h2>Configuración de Firebase</h2>
      <FirebaseConfigForm />
    </div>
  );
}

function FirstSteps() {
  return (
    <div>
      <h2>Primeros pasos</h2>
      <p>Ingresa la clave de Firebase para habilitar las notificaciones.</p>
      <FirebaseConfigForm />
    </div>
  );
}

function Welcome({ onDone }) {
  return (
    <div>
      <h2>Bienvenido a BizonMDM</h2>
      <p>Desde aquí puedes aprovisionar dispositivos por QR, gestionar políticas y más.</p>
      <button onClick={onDone}>Comenzar</button>
    </div>
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

const PERMISSIONS = ['wipe', 'reboot', 'lock', 'screenshot'];

function ClientManager() {
  const [clients, setClients] = useState([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [perms, setPerms] = useState([]);
  const [assign, setAssign] = useState({});

  const fetchClients = () => apiFetch('/admin/clients').then(setClients).catch(console.error);
  useEffect(fetchClients, []);

  const toggle = (perm, list, setter) => {
    if (list.includes(perm)) setter(list.filter(p => p !== perm));
    else setter([...list, perm]);
  };

  const createClient = (e) => {
    e.preventDefault();
    apiFetch('/admin/clients', {
      method: 'POST',
      body: JSON.stringify({ username, password, permissions: perms })
    }).then(() => { setUsername(''); setPassword(''); setPerms([]); fetchClients(); }).catch(console.error);
  };

  const updatePerms = (id, permissions) => {
    apiFetch(`/admin/clients/${id}`, { method: 'PUT', body: JSON.stringify({ permissions }) })
      .then(fetchClients).catch(console.error);
  };

  const assignDevice = (id) => {
    const deviceId = assign[id];
    if (!deviceId) return;
    const client = clients.find(c => c.id === id);
    const devices = [...client.devices, deviceId];
    apiFetch(`/admin/clients/${id}`, { method: 'PUT', body: JSON.stringify({ devices }) })
      .then(() => { setAssign({ ...assign, [id]: '' }); fetchClients(); }).catch(console.error);
  };

  const deleteClient = (id) => {
    apiFetch(`/admin/clients/${id}`, { method: 'DELETE' }).then(fetchClients).catch(console.error);
  };

  return (
    <div>
      <h2>Clientes</h2>
      <form onSubmit={createClient} style={{ marginBottom: '1rem' }}>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Usuario" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" />
        <div>
          {PERMISSIONS.map(p => (
            <label key={p} style={{ marginRight: '0.5rem' }}>
              <input type="checkbox" checked={perms.includes(p)} onChange={() => toggle(p, perms, setPerms)} /> {p}
            </label>
          ))}
        </div>
        <button type="submit">Crear</button>
      </form>
      <table>
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Dispositivos</th>
            <th>Permisos</th>
            <th>Asignar dispositivo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {clients.map(c => (
            <tr key={c.id}>
              <td>{c.username}</td>
              <td>{c.devices.join(', ')}</td>
              <td>
                {PERMISSIONS.map(p => (
                  <label key={p} style={{ marginRight: '0.5rem' }}>
                    <input
                      type="checkbox"
                      checked={c.permissions.includes(p)}
                      onChange={() => {
                        const np = c.permissions.includes(p)
                          ? c.permissions.filter(pr => pr !== p)
                          : [...c.permissions, p];
                        updatePerms(c.id, np);
                      }}
                    /> {p}
                  </label>
                ))}
              </td>
              <td>
                <input value={assign[c.id] || ''} onChange={e => setAssign({ ...assign, [c.id]: e.target.value })} placeholder="deviceId" />
                <button type="button" onClick={() => assignDevice(c.id)}>Asignar</button>
              </td>
              <td><button type="button" onClick={() => deleteClient(c.id)}>Eliminar</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.hash || '#/dashboard');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [welcome, setWelcome] = useState(!localStorage.getItem('welcomeSeen'));
  const [tenantConfig, setTenantConfig] = useState({});

  useEffect(() => {
    const sub = window.location.hostname.split('.')[0];
    fetch(`/api/config/tenant/${sub}`)
      .then(r => r.ok ? r.json() : {})
      .then(setTenantConfig)
      .catch(() => setTenantConfig({}));
  }, []);

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

  if (welcome && route !== '#/first-steps') {
    return <Welcome onDone={() => { localStorage.setItem('welcomeSeen', '1'); setWelcome(false); }} />;
  }

  let page;
  if (route === '#/dashboard') page = <Dashboard />;
  else if (route === '#/dashboard/finance') page = <FinancialDashboard />;
  else if (route === '#/devices') page = <DeviceTable onSelect={(id) => window.location.hash = `#/devices/${id}`} />;
  else if (route.startsWith('#/devices/')) {
    const id = route.split('/')[2];
    page = <DeviceDetails id={id} onBack={() => window.location.hash = '#/devices'} />;
  } else if (route === '#/policies') page = <PolicyEditor />;
  else if (route === '#/clients') page = <ClientManager />;
  else if (route === '#/admin/clients') page = <StoreUserManager />;
  else if (route === '#/admin/logs') page = <AuditLogs />;
  else if (route === '#/config') page = <Config />;
  else if (route === '#/first-steps') page = <FirstSteps />;
  else page = <Dashboard />;

  return (
    <div>
      <header>
        <h1>{tenantConfig.title || 'Bizon MDM Admin'}</h1>
        <nav>
          <a href="#/dashboard">Dashboard</a>
          <a href="#/dashboard/finance">Finanzas</a>
          <a href="#/devices">Dispositivos</a>
          <a href="#/policies">Políticas</a>
          <a href="#/clients">Clientes</a>
          <a href="#/admin/clients">Tiendas y usuarios</a>
          <a href="#/admin/logs">Logs</a>
          <a href="#/config">Config</a>
        </nav>
        <ServerStatus />
        <input value={token} onChange={handleTokenChange} placeholder="JWT token" style={{ marginLeft: '1rem' }} />
      </header>
      <main style={{ padding: '1rem' }}>
        {page}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
