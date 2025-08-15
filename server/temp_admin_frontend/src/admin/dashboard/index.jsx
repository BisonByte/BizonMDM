import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import { apiFetch } from '../../App.jsx'; // Assuming App.jsx is in the same directory

function FinancialDashboard() {
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    if (apiFetch) {
      apiFetch('/api/contracts/summary')
        .then(setSummary)
        .catch(() => setSummary(null));
      apiFetch('/devices')
        .then(setDevices)
        .catch(() => setDevices([]));
    }
  }, []);

  const alerts = [];
  devices.forEach(d => {
    const s = d.status || {};
    if (s.battery && s.battery < 20) alerts.push('b');
    if (s.rootAttempt) alerts.push('r');
    if (s.wipeDetected) alerts.push('w');
    if (s.bootloaderTampered) alerts.push('t');
  });

  const data = summary ? [
    { name: 'Total', value: summary.total },
    { name: 'Vencidos', value: summary.overdue },
    { name: 'Pagados', value: summary.paid },
  ] : [];

  const cardStyle = {
    background: '#fff',
    padding: '1rem',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    flex: '1',
    minWidth: '150px'
  };

  if (!summary && !devices.length) return <div><h2>Dashboard</h2><p>Sin datos</p></div>;

  return (
    <div>
      <h2>Dashboard</h2>
      <div style={{display:'flex', gap:'1rem', marginBottom:'1rem', flexWrap:'wrap'}}>
        <motion.div style={cardStyle} initial={{opacity:0, y:10}} animate={{opacity:1, y:0}}>
          <h3>Dispositivos Activos</h3>
          <p>{devices.length}</p>
        </motion.div>
        <motion.div style={cardStyle} initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} transition={{delay:0.1}}>
          <h3>Alertas</h3>
          <p>{alerts.length}</p>
        </motion.div>
        <motion.div style={cardStyle} initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} transition={{delay:0.2}}>
          <h3>Pagos Vencidos</h3>
          <p>{summary?.overdue || 0}</p>
        </motion.div>
      </div>
      {summary && (
        <motion.div initial={{opacity:0}} animate={{opacity:1}}>
          <BarChart width={400} height={250} data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#8884d8" isAnimationActive={true} />
          </BarChart>
        </motion.div>
      )}
    </div>
  );
}

export default FinancialDashboard;