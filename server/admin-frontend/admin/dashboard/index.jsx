const { useState, useEffect } = React;
const { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } = Recharts;

function FinancialDashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (window.apiFetch) {
      window.apiFetch('/api/contracts/summary')
        .then(setSummary)
        .catch(() => setSummary(null));
    }
  }, []);

  if (!summary) return <div><h2>Contratos</h2><p>Sin datos</p></div>;

  const data = [
    { name: 'Total', value: summary.total },
    { name: 'Vencidos', value: summary.overdue },
    { name: 'Pagados', value: summary.paid },
  ];

  return (
    <div>
      <h2>Contratos</h2>
      <BarChart width={400} height={250} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
    </div>
  );
}

window.FinancialDashboard = FinancialDashboard;
