export async function uploadExperiment(payload: any) {
  const res = await fetch(`/experiments/upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export default { uploadExperiment };
