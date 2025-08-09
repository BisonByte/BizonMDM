export function calculateInstallment(amount, interestRate, term) {
  const monthlyRate = interestRate / 12 / 100;
  if (monthlyRate === 0) {
    return amount / term;
  }
  return (
    amount *
    ((monthlyRate * Math.pow(1 + monthlyRate, term)) /
      (Math.pow(1 + monthlyRate, term) - 1))
  );
}

export function simulateSchedule(amount, interestRate, term) {
  const installment = calculateInstallment(amount, interestRate, term);
  const schedule = [];
  for (let i = 1; i <= term; i++) {
    schedule.push({ installment: i, amount: installment });
  }
  return { installment, schedule };
}
