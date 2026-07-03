import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { PlaygroundPage } from "./pages/PlaygroundPage";
import { RunsPage } from "./pages/RunsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/playground" element={<PlaygroundPage />} />
        <Route path="/runs" element={<RunsPage />} />
      </Route>
    </Routes>
  );
}
