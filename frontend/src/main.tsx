import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import "./styles.css";
import SetsPage from "./pages/SetsPage";
import SetPage from "./pages/SetPage";
import ImportPage from "./pages/ImportPage";

function App() {
  return (
    <BrowserRouter>
      <header className="topbar">
        <span className="brand">TCG Collection</span>
        <nav>
          <NavLink to="/" end>Set</NavLink>
          <NavLink to="/import">Importa</NavLink>
        </nav>
      </header>
      <main className="wrap">
        <Routes>
          <Route path="/" element={<SetsPage />} />
          <Route path="/sets/:id" element={<SetPage />} />
          <Route path="/import" element={<ImportPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
