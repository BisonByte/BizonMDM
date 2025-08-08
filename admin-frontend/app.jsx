const { useState, useEffect } = React;

function Dashboard() {
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Resumen visual de la flota de dispositivos.</p>
    </div>
  );
}

function DeviceTable({ onSelect }) {
  const devices = [
    { id: 1, imei: '123456789012345', model: 'Pixel 5', serial: 'ABC123', status: 'Activo' },
    { id: 2, imei: '987654321098765', model: 'Galaxy S21', serial: 'XYZ987', status: 'Inactivo' }
  ];
  return (
    <div>
      <h2>Dispositivos</h2>
      <input placeholder="Buscar..." />
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
          {devices.map(d => (
            <tr key={d.id} onClick={() => onSelect(d.id)} style={{ cursor: 'pointer' }}>
              <td>{d.imei}</td>
              <td>{d.model}</td>
              <td>{d.serial}</td>
              <td>{d.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DeviceDetails({ id, onBack }) {
  return (
    <div>
      <h2>Dispositivo {id}</h2>
      <p>Información detallada del dispositivo.</p>
      <div className="actions">
        <button>Borrar Datos</button>
        <button>Reiniciar</button>
      </div>
      <h3>Historial de Logs</h3>
      <ul>
        <li>Log 1...</li>
        <li>Log 2...</li>
      </ul>
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

  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash || '#/dashboard');
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

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
      </header>
      <main style={{ padding: '1rem' }}>
        {page}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
