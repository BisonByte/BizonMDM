const { useState, useEffect } = React;

const API_BASE = '/api/client';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('clientToken');
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
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Dispositivos registrados: {total}</p>
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
  const [qrSrc, setQrSrc] = useState(null);
  const [showQr, setShowQr] = useState(false);
  useEffect(() => {
    apiFetch(`/devices/${id}`).then(setInfo).catch(console.error);
  }, [id]);
  const sendCommand = async (action) => {
    try {
      await apiFetch(`/device/${action}`, {
        method: 'POST',
        body: JSON.stringify({ deviceId: id })
      });
      alert('Comando enviado');
    } catch (e) {
      alert('Error enviando comando');
    }
  };
  const fetchQr = async () => {
    try {
      const res = await fetch(`/provisioning/qr/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('clientToken') || ''}`
        }
      });
      if (!res.ok) throw new Error('QR error');
      const blob = await res.blob();
      setQrSrc(URL.createObjectURL(blob));
      setShowQr(true);
    } catch (e) {
      alert('No se pudo obtener el QR');
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
        <button onClick={fetchQr}>Mostrar QR</button>
      </div>
      <h3>Historial de Logs</h3>
      <DeviceLogs id={id} />
      <button onClick={onBack}>Volver</button>
      {showQr && qrSrc && (
        <div
          className="qr-modal"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onClick={() => setShowQr(false)}
        >
          <div style={{ background: '#fff', padding: '1rem' }} onClick={e => e.stopPropagation()}>
            <img src={qrSrc} alt="QR de aprovisionamiento" style={{ maxWidth: '100%' }} />
            <div>
              <a href={qrSrc} download={`qr-${id}.png`}>Descargar QR</a>
            </div>
            <h4>Instalación en Android</h4>
            <ol>
              <li>Abrir la app de cámara o escáner QR.</li>
              <li>Escanear el código y abrir el enlace.</li>
              <li>Seguir las instrucciones para instalar Bizon MDM.</li>
            </ol>
            <button onClick={() => setShowQr(false)}>Cerrar</button>
          </div>
        </div>
      )}
    </div>
  );
}

function DomainSetup() {
  const [domain, setDomain] = useState('');
  const [apiUser, setApiUser] = useState('');
  const [apiPassword, setApiPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const domainRegex = /^(?!-)(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.)+[A-Za-z]{2,}$/;
    if (!domainRegex.test(domain)) {
      setError('Dominio inválido');
      return;
    }
    try {
      await apiFetch('/domain', {
        method: 'POST',
        body: JSON.stringify({ domain, apiUser, apiPassword })
      });
      window.location.hash = '#/dashboard';
    } catch (err) {
      setError('No se pudo conectar');
    }
  };

  return (
    <div>
      <h2>Configurar Dominio</h2>
      <form onSubmit={handleSubmit}>
        <input value={domain} onChange={e => setDomain(e.target.value)} placeholder="Dominio" />
        <input value={apiUser} onChange={e => setApiUser(e.target.value)} placeholder="Usuario API" />
        <input type="password" value={apiPassword} onChange={e => setApiPassword(e.target.value)} placeholder="Contraseña API" />
        <button type="submit">Guardar</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.hash || '#/dashboard');
  const [token, setToken] = useState(localStorage.getItem('clientToken') || '');
  const [clientInfo, setClientInfo] = useState(null);

  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash || '#/dashboard');
    window.addEventListener('hashchange', onHashChange);
    apiFetch('/info').then(setClientInfo).catch(console.error);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleTokenChange = (e) => {
    const v = e.target.value;
    setToken(v);
    localStorage.setItem('clientToken', v);
  };

  let page;
  if (route === '#/dashboard') page = <Dashboard />;
  else if (route === '#/domain') page = <DomainSetup />;
  else if (route === '#/devices') page = <DeviceTable onSelect={(id) => window.location.hash = `#/devices/${id}`} />;
  else if (route.startsWith('#/devices/')) {
    const id = route.split('/')[2];
    page = <DeviceDetails id={id} onBack={() => window.location.hash = '#/devices'} />;
  } else page = <Dashboard />;

  return (
    <div>
      <header>
        {clientInfo?.logo && <img src={clientInfo.logo} alt="logo" style={{ height: '40px', verticalAlign: 'middle', marginRight: '0.5rem' }} />}
        <h1 style={{ display: 'inline-block', margin: 0 }}>{clientInfo?.name || 'Bizon MDM'}</h1>
        <nav>
          <a href="#/dashboard">Dashboard</a>
          <a href="#/domain">Dominio</a>
          <a href="#/devices">Dispositivos</a>
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

