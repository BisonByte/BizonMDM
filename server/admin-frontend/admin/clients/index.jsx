const { useState, useEffect } = React;

const PERMISSIONS = ['dispositivos', 'contratos'];

function StoreUserManager() {
  const [stores, setStores] = useState([]);
  const [storeName, setStoreName] = useState('');
  const [users, setUsers] = useState([]);
  const [username, setUsername] = useState('');
  const [perms, setPerms] = useState([]);

  useEffect(() => {
    if (window.apiFetch) {
      window.apiFetch('/api/stores').then(setStores).catch(() => setStores([]));
      window.apiFetch('/api/users').then(setUsers).catch(() => setUsers([]));
    }
  }, []);

  function createStore(e) {
    e.preventDefault();
    if (!window.apiFetch) return;
    window.apiFetch('/api/stores', { method: 'POST', body: JSON.stringify({ name: storeName }) })
      .then(s => setStores([...stores, s]))
      .catch(() => {})
      .finally(() => setStoreName(''));
  }

  function createUser(e) {
    e.preventDefault();
    if (!window.apiFetch) return;
    const body = { username, permissions: perms };
    window.apiFetch('/api/users', { method: 'POST', body: JSON.stringify(body) })
      .then(u => setUsers([...users, u]))
      .catch(() => {})
      .finally(() => { setUsername(''); setPerms([]); });
  }

  const toggle = (p) => {
    setPerms(perms.includes(p) ? perms.filter(x => x !== p) : [...perms, p]);
  };

  return (
    <div>
      <h2>Tiendas</h2>
      <form onSubmit={createStore} style={{ marginBottom: '1rem' }}>
        <input value={storeName} onChange={e => setStoreName(e.target.value)} placeholder="Nombre" />
        <button type="submit">Agregar</button>
      </form>
      <ul>
        {stores.map(s => <li key={s.id}>{s.name}</li>)}
      </ul>

      <h2>Usuarios</h2>
      <form onSubmit={createUser} style={{ marginBottom: '1rem' }}>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Usuario" />
        <div>
          {PERMISSIONS.map(p => (
            <label key={p} style={{ marginRight: '0.5rem' }}>
              <input type="checkbox" checked={perms.includes(p)} onChange={() => toggle(p)} /> {p}
            </label>
          ))}
        </div>
        <button type="submit">Crear</button>
      </form>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.username} - {u.permissions.join(', ')}</li>
        ))}
      </ul>
    </div>
  );
}

window.StoreUserManager = StoreUserManager;
