const { useState, useEffect } = React;

function FinancialDashboard() {
  const [data, setData] = useState({});

  useEffect(() => {
    if (window.apiFetch) {
      window.apiFetch('/api/finance')
        .then(setData)
        .catch(() => setData({}));
    }
  }, []);

  return (
    <div>
      <h2>Indicadores financieros</h2>
      <ul>
        <li>Ingresos: {data.revenue ?? 'N/D'}</li>
        <li>Gastos: {data.expenses ?? 'N/D'}</li>
        <li>Beneficio: {data.profit ?? 'N/D'}</li>
      </ul>
    </div>
  );
}

window.FinancialDashboard = FinancialDashboard;
