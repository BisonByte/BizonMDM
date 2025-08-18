const { useState, useEffect } = React;

const API_BASE = process.env.API_BASE || '';

async function apiFetch(path, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  const csrfMatch = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
  if (csrfMatch) headers['X-CSRF-Token'] = csrfMatch[1];
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(API_BASE + path, { ...options, headers, credentials: 'include' });
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
  const color = ok ? '#16a34a' : '#dc2626';
  return <span className="status-dot" title={`DB:${status?.database ? 'ok' : 'fail'} Firebase:${status?.firebase ? 'ok' : 'fail'}`} style={{ backgroundColor: color }} />;
}

function Dashboard() {
  const [devices, setDevices] = useState([]);
  useEffect(() => {
    apiFetch('/admin/devices').then(setDevices).catch(console.error);
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
    if (s.bootloaderTampered) alerts.push(`Bootloader alterado en ${d.deviceId}`);
  });
  // Build small sparkline data
  const trend = Array.from({length: 12}, (_,i)=>({x:i, y: Math.max(0, total + (i%3-1)*Math.ceil(total*0.1))}));
  return (
    <div className="container">
      <div className="kpi-grid">
        <div className="card gradient card-stat">
          <h4>Dispositivos</h4>
          <div className="value">{total}</div>
          <div className="chip">Total</div>
        </div>
        <div className="card gradient card-stat">
          <h4>Modelos</h4>
          <div className="value">{Object.keys(modelCounts).length}</div>
          <div className="chip">Únicos</div>
        </div>
        <div className="card gradient card-stat">
          <h4>Alertas</h4>
          <div className="value">{alerts.length}</div>
          <div className="chip">Últimas 24h</div>
        </div>
        <div className="card gradient card-stat">
          <h4>Salud</h4>
          <div className="value">{Math.max(0, 100 - alerts.length)}</div>
          <div className="chip">Score</div>
        </div>
      </div>
      <div className="grid cols-3" style={{marginTop:'1rem'}}>
        <div className="card">
          <h3>Distribución de Modelos</h3>
          <ul style={{ margin: 0, paddingLeft: '1rem' }}>
            {Object.entries(modelCounts).map(([m, c]) => (
              <li key={m}>{m}: {c}</li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Alertas recientes</h3>
          <div className="muted" style={{display:'grid', gap:'.35rem'}}>
            {alerts.slice(0,6).map((a,i)=> <div key={i} className="chip">{a}</div>)}
            {alerts.length===0 && <span className="muted">Sin alertas</span>}
          </div>
        </div>
        <div className="card">
          <h3>Tendencia</h3>
          <svg width="100%" height="120" viewBox="0 0 120 40" preserveAspectRatio="none">
            <polyline fill="none" stroke="var(--primary)" strokeWidth="2" points={trend.map((p,i)=> `${(i/11)*120},${40 - (p.y/(total||1))*30 - 5}`).join(' ')} />
          </svg>
        </div>
      </div>
    </div>
  );
}

function DeviceTable({ onSelect }) {
  const [devices, setDevices] = useState([]);
  const [search, setSearch] = useState('');
  useEffect(() => {
    apiFetch('/admin/devices').then(setDevices).catch(console.error);
  }, []);
  const filtered = devices.filter(d =>
    [d.deviceId, d.imei, d.model, d.serial]
      .filter(Boolean)
      .some(v => v.toLowerCase().includes(search.toLowerCase()))
  );
  return (
    <div className="container">
      <div className="card">
        <h2>Dispositivos</h2>
        <input className="input" placeholder="Buscar..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>
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
              <td>
                {d.status?.battery ? `Bat ${d.status.battery}%` : ''}
                {d.status?.rootAttempt ? ' Root' : ''}
                {d.status?.wipeDetected ? ' Wipe' : ''}
                {d.status?.bootloaderTampered ? ' Boot' : ''}
              </td>
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
    apiFetch(`/admin/logs/${id}`).then(d => setLogs(d.logs || [])).catch(console.error);
  }, [id]);
  if (!logs.length) return <div className="card"><p className="muted">Sin registros</p></div>;
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
    apiFetch('/admin/config/fcm').then(d => setKey(d.key || '')).catch(console.error);
  }, []);
  const save = () => {
    apiFetch('/admin/config/fcm', { method: 'POST', body: JSON.stringify({ key }) })
      .then(() => setMessage('Clave de Firebase guardada correctamente'))
      .catch(() => setMessage('Error al guardar la clave'));
  };
  const test = () => {
    apiFetch('/admin/test-fcm', { method: 'POST' })
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
    <div className="container">
      <div className="card">
        <h2>Configuración de Firebase</h2>
        <FirebaseConfigForm />
      </div>
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
  const [lockMsg, setLockMsg] = useState('');
  const [pkg, setPkg] = useState('');
  useEffect(() => {
    apiFetch(`/admin/devices/${id}`).then(setInfo).catch(console.error);
  }, [id]);
  const sendCommand = async (action) => {
    try {
      const path = `/admin/device/${action}`;
      const body = action === 'lock' && lockMsg ? { deviceId: id, message: lockMsg } : { deviceId: id };
      await apiFetch(path, { method: 'POST', body: JSON.stringify(body) });
      alert('Comando enviado');
    } catch (e) {
      alert('Error enviando comando');
    }
  };
  const hideApp = async () => {
    if (!pkg) return alert('Ingresa el package');
    try {
      await apiFetch('/admin/device/hide-app', { method: 'POST', body: JSON.stringify({ deviceId: id, package: pkg }) });
      alert('Comando enviado');
    } catch (e) { alert('Error enviando comando'); }
  };
  const hideAll = async () => {
    try {
      await apiFetch('/admin/device/hide-all', { method: 'POST', body: JSON.stringify({ deviceId: id }) });
      alert('Comando enviado');
    } catch (e) { alert('Error enviando comando'); }
  };
  return (
    <div className="container">
      <div className="card">
        <h2>Dispositivo {id}</h2>
        {info && (
          <div className="grid">
            <div className="muted">Modelo<br/><strong>{info.model}</strong></div>
            <div className="muted">Serial<br/><strong>{info.serial}</strong></div>
            <div className="muted">IMEI<br/><strong>{info.imei}</strong></div>
            <div className="muted">Batería<br/><strong>{info.status?.battery ?? 'N/A'}%</strong></div>
            <div className="muted">Root<br/><strong>{info.status?.rootAttempt ? 'Sí' : 'No'}</strong></div>
            <div className="muted">Wipe<br/><strong>{info.status?.wipeDetected ? 'Sí' : 'No'}</strong></div>
          </div>
        )}
      </div>
      <div className="card">
        <h3>Acciones</h3>
        <div className="actions">
          <button className="btn-danger" onClick={() => sendCommand('wipe')}>Borrar Datos</button>
          <button className="btn-warning" onClick={() => sendCommand('reboot')}>Reiniciar</button>
          <input className="input" value={lockMsg} onChange={e => setLockMsg(e.target.value)} placeholder="Mensaje de bloqueo" />
          <button className="btn-primary" onClick={() => sendCommand('lock')}>Bloquear</button>
          <button onClick={() => sendCommand('screenshot')}>Tomar Captura</button>
          <input className="input" value={pkg} onChange={e => setPkg(e.target.value)} placeholder="com.paquete.app" />
          <button onClick={hideApp}>Ocultar App</button>
          <button onClick={hideAll}>Ocultar Todas</button>
        </div>
      </div>
      <div className="card">
        <h3>Historial de Logs</h3>
        <DeviceLogs id={id} />
      </div>
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
    <div className="container">
      <div className="card">
        <h2>Clientes</h2>
        <form onSubmit={createClient} style={{ display:'flex', gap:'.5rem', flexWrap:'wrap', marginBottom: '1rem' }}>
          <input className="input" value={username} onChange={e => setUsername(e.target.value)} placeholder="Usuario" />
          <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" />
          <div className="muted" style={{ display:'flex', gap:'.5rem', alignItems:'center', flexWrap:'wrap' }}>
            {PERMISSIONS.map(p => (
              <label key={p} style={{ marginRight: '0.5rem' }}>
                <input type="checkbox" checked={perms.includes(p)} onChange={() => toggle(p, perms, setPerms)} /> {p}
              </label>
            ))}
          </div>
          <button className="btn-primary" type="submit">Crear</button>
        </form>
      </div>
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
                <input className="input" value={assign[c.id] || ''} onChange={e => setAssign({ ...assign, [c.id]: e.target.value })} placeholder="deviceId" />
                <button className="btn-primary" type="button" onClick={() => assignDevice(c.id)}>Asignar</button>
              </td>
              <td><button className="btn-danger" type="button" onClick={() => deleteClient(c.id)}>Eliminar</button></td>
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
  const [theme, setTheme] = useState(document.documentElement.getAttribute('data-theme') || 'light');

  useEffect(() => {
    const sub = window.location.hostname.split('.')[0];
    apiFetch(`/admin/config/tenant/${sub}`)
      .then(setTenantConfig)
      .catch(() => setTenantConfig({}));
  }, []);

  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash || '#/dashboard');
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('theme', theme); } catch(e) {}
  }, [theme]);

  const handleTokenChange = (e) => {
    const v = e.target.value;
    setToken(v);
    localStorage.setItem('token', v);
  };

  const quickLogin = async () => {
    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'admin' }),
        credentials: 'include'
      });
      if(!res.ok){ throw new Error('login'); }
      const data = await res.json();
      const tok = data.token;
      setToken(tok);
      localStorage.setItem('token', tok);
      alert('Autenticado como admin');
    } catch (e) {
      alert('No se pudo iniciar sesión. Asegúrate de haber creado el usuario admin/admin.');
    }
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

  const link = (href, label, icon) => (
    <a href={href} className={`nav-item ${(route === href || route.startsWith(href + '/')) ? 'active' : ''}`}>
      <span className="icon">{icon}</span>
      <span>{label}</span>
    </a>
  );
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-badge">B</div>
          <div>{tenantConfig.title || 'Bizon MDM'}</div>
        </div>
        <nav>
          {link('#/dashboard', 'Dashboard', '🏠')}
          {link('#/dashboard/finance', 'Finanzas', '📈')}
          {link('#/devices', 'Dispositivos', '📱')}
          {link('#/policies', 'Políticas', '⚙️')}
          {link('#/clients', 'Clientes', '👥')}
          {link('#/admin/clients', 'Tiendas y usuarios', '🏬')}
          {link('#/admin/logs', 'Logs', '🧾')}
          {link('#/config', 'Config', '🔧')}
        </nav>
      </aside>
      <section className="content">
        <div className="topbar">
          <div className="brand">Panel</div>
          <div className="search"><input placeholder="Buscar…" /></div>
          <div className="spacer" />
          <ServerStatus />
          <select className="token-input" value={theme} onChange={(e)=>setTheme(e.target.value)} style={{minWidth:'auto'}} title="Tema">
            <option value="light">Claro</option>
            <option value="dark">Oscuro</option>
          </select>
          <input className="token-input" value={token} onChange={handleTokenChange} placeholder="JWT token" />
          <button className="btn-primary" onClick={quickLogin} title="Login rápido admin/admin">Login</button>
          <div className="avatar" />
        </div>
        <main>
          {page}
        </main>
      </section>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);

// --- Missing component stubs and small features ---
function FinancialDashboard() {
  const [data, setData] = useState(null);
  useEffect(() => {
    apiFetch('/admin/contracts/summary').then(setData).catch(() => setData(null));
  }, []);
  if (!data) return <p>Cargando…</p>;
  return (
    <div>
      <h2>Finanzas</h2>
      <ul>
        <li>Contratos: {data.total}</li>
        <li>Pagos vencidos: {data.overdue}</li>
        <li>Pagos realizados: {data.paid}</li>
      </ul>
    </div>
  );
}

function StoreUserManager() {
  const [stores, setStores] = useState([]);
  const [users, setUsers] = useState([]);
  const [name, setName] = useState('');
  const [newUser, setNewUser] = useState({ username: '', password: '', store_id: '' });
  const refresh = () => {
    apiFetch('/api/stores').then(setStores).catch(() => setStores([]));
    apiFetch('/api/users').then(setUsers).catch(() => setUsers([]));
  };
  useEffect(refresh, []);
  const addStore = async (e) => {
    e.preventDefault();
    await apiFetch('/api/stores', { method: 'POST', body: JSON.stringify({ name }) }).catch(() => {});
    setName(''); refresh();
  };
  const addUser = async (e) => {
    e.preventDefault();
    await apiFetch('/api/users', { method: 'POST', body: JSON.stringify(newUser) }).catch(() => {});
    setNewUser({ username: '', password: '', store_id: '' }); refresh();
  };
  return (
    <div>
      <h2>Tiendas</h2>
      <form onSubmit={addStore}>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Nombre de tienda" />
        <button>Agregar</button>
      </form>
      <ul>{stores.map(s => <li key={s.id}>{s.name} (id {s.id})</li>)}</ul>
      <h2>Usuarios</h2>
      <form onSubmit={addUser}>
        <input value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} placeholder="Usuario" />
        <input type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} placeholder="Contraseña" />
        <input value={newUser.store_id} onChange={e => setNewUser({ ...newUser, store_id: Number(e.target.value) || '' })} placeholder="Store ID" />
        <button>Crear</button>
      </form>
      <ul>{users.map(u => <li key={u.id}>{u.username} (store {u.store_id})</li>)}</ul>
    </div>
  );
}

function AuditLogs() {
  return (
    <div>
      <h2>Logs del sistema</h2>
      <p>Esta sección mostrará logs de auditoría en futuras versiones.</p>
    </div>
  );
}
