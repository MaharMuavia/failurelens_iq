import { useState } from "react";
import { ManagerDashboard } from "./components/ManagerDashboard";

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("Analysis");

  return <ManagerDashboard activeTab={activeTab} onTabChange={setActiveTab} />;
}

