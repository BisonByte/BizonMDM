import { useState, useEffect } from 'react';
import { apiFetch } from '../../App.jsx'; // Assuming App.jsx is in the same directory

const PERMISSIONS = ['dispositivos', 'contratos'];

function StoreUserManager() {
  const [stores, setStores] = useState([]);
  const [storeName, setStoreName] = useState('');
  const [users, setUsers] = useState([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [storeId, setStoreId] = useState('');
  const [perms, setPerms] = useState([]);
  const [editing, setEditing] = useState(null);
  const [editDomain, setEditDomain] = useState('');
  const [editApiUser, setEditApiUser] = useState('');
  const [editApiPassword, setEditApiPassword] = useState('');

  useEffect(() => {
    if (apiFetch) {
      apiFetch('/api/stores')
        .then(async sts => {
          const detailed = await Promise.all(
            sts.map(async s => {
              try {
                const info = await apiFetch(`/api/stores/${s.id}/domain`);
                return { ...s, domain: info.domain, apiUser: info.api_user, connected: info.connected !== false, logs: info.logs || [] };
              } catch (err) {
                return { ...s, connected: false, logs: [] };
              }
            })
          );
          setStores(detailed);
        })
        .catch(() => setStores([]));
      apiFetch('/api/users').then(setUsers).catch(() => setUsers([]));
    }
  }, []);

  function createStore(e) {
    e.preventDefault();
    if (!apiFetch) return;
    apiFetch('/api/stores', { method: 'POST', body: JSON.stringify({ name: storeName }) })
      .then(s => setStores([...stores, s]))
      .catch(() => {})
      .finally(() => setStoreName(''));
  }

  function createUser(e) {
    e.preventDefault();
    if (!apiFetch) return;
    if (!storeId || users.some(u => u.store_id === Number(storeId))) return;
    const body = { username, password, store_id: Number(storeId), permissions: perms };
    apiFetch('/api/users', { method: 'POST', body: JSON.stringify(body) })
      .then(u => setUsers([...users, u]))
      .catch(() => {})
      .finally(() => { setUsername(''); setPassword(''); setStoreId(''); setPerms([]); });
  }

  const toggle = (p) => {
    setPerms(perms.includes(p) ? perms.filter(x => x !== p) : [...perms, p]);
  };

  function startEdit(store) {
    setEditing(store.id);
    setEditDomain(store.domain || '');
    setEditApiUser(store.apiUser || '');
    setEditApiPassword('');
  }

  function cancelEdit() {
    setEditing(null);
    setEditDomain('');
    setEditApiUser('');
    setEditApiPassword('');
  }

  function saveEdit(e) {
    e.preventDefault();
    if (!apiFetch || editing == null) return;
    const id = editing;
    const body = { domain: editDomain, api_user: editApiUser };
    if (editApiPassword) body.api_password = editApiPassword;
    apiFetch(`/api/stores/${id}/domain`, { method: 'POST', body: JSON.stringify(body) })
      .then(info => {
        setStores(stores.map(s => s.id === id ? { ...s, domain: info.domain, apiUser: info.api_user, connected: info.connected !== false, logs: info.logs || [] } : s));
        cancelEdit();
      })
      .catch(() => {
        setStores(stores.map(s => s.id === id ? { ...s, connected: false } : s));
      });
  }

  return (
    <div>
      <h2>Tiendas</h2>
      <form onSubmit={createStore} style={{ marginBottom: '1rem' }}>
        <input value={storeName} onChange={e => setStoreName(e.target.value)} placeholder="Nombre" />
        <button type="submit">Agregar</button>
      </form>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Dominio</th>
            <th>Usuario API</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {stores.map(s => (
            <React.Fragment key={s.id}>
              <tr>
                <td>{s.name}</td>
                <td>{s.domain || '-'}</td>
                <td>{s.apiUser || '-'}</td>
                <td>{s.connected ? '✅' : <span style={{ color: 'red' }}>❌{s.logs && s.logs.length ? ` (${s.logs.length})` : ''}</span>}</td>
                <td>
                  {editing === s.id ? (
                    <form onSubmit={saveEdit} style={{ display: 'inline' }}>
                      <input value={editDomain} onChange={e => setEditDomain(e.target.value)} placeholder="Dominio" />
                      <input value={editApiUser} onChange={e => setEditApiUser(e.target.value)} placeholder="Usuario API" />
                      <input type="password" value={editApiPassword} onChange={e => setEditApiPassword(e.target.value)} placeholder="Contraseña" />
                      <button type="submit">Guardar</button>
                      <button type="button" onClick={cancelEdit}>Cancelar</button>
                    </form>
                  ) : (
                    <button onClick={() => startEdit(s)}>Editar</button>
                  )}
                </td>
              </tr>
              {!s.connected && s.logs && s.logs.length > 0 && (
                <tr>
                  <td colSpan="5">
                    <table style={{ width: '100%' }}>
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Mensaje</th>
                        </tr>
                      </thead>
                      <tbody>
                        {s.logs.map((l, i) => (
                          <tr key={i}>
                            <td>{l.date || l.timestamp || '-'}</td>
                            <td>{l.message || JSON.stringify(l)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>

      <h2>Usuarios</h2>
      <form onSubmit={createUser} style={{ marginBottom: '1rem' }}>
        <select value={storeId} onChange={e => setStoreId(e.target.value)}>
          <option value="">Tienda</option>
          {stores.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Usuario" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" />
        <div>
          {PERMISSIONS.map(p => (
            <label key={p} style={{ marginRight: '0.5rem' }}>
              <input type="checkbox" checked={perms.includes(p)} onChange={() => toggle(p)} /> {p}
            </label>
          ))}
        </div>
        <button type="submit" disabled={!storeId || users.some(u => u.store_id === Number(storeId))}>Crear</button>
      </form>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.username} - tienda {u.store_id}</li>
        ))}
      </ul>
    </div>
  );
}

export default StoreUserManager;