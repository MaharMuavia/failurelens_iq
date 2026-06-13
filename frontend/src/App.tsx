import { useState } from "react";
import AuthScreen from "./components/AuthScreen";

export default function App() {
  const guest = localStorage.getItem("failurelens_guest_mode") === "true";
  if (!guest) {
    return <AuthScreen />;
  }
  // Fallback: if guest mode already set, show the existing dashboard component which is imported inside AuthScreen when needed
  return <AuthScreen />;
}

