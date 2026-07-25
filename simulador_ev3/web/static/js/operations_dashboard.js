(async () => {
  const status = document.getElementById("operationsStatus");
  const output = document.getElementById("operationsData");
  try {
    const health = await fetch("/healthz").then((response) => response.json());
    const metrics = await fetch("/metrics").then((response) => response.json());
    status.textContent = `Estado: ${health.status}`;
    output.textContent = JSON.stringify({ health, metrics }, null, 2);
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
})();
