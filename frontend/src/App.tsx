import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AnalysisResultPage from "./pages/AnalysisResultPage";
import CommunityPage from "./pages/CommunityPage";
import IncidentDetailsPage from "./pages/IncidentDetailsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/incidents/:incidentId/result" element={<AnalysisResultPage />} />
        <Route path="/incidents/:incidentId" element={<IncidentDetailsPage />} />
        <Route path="/community" element={<CommunityPage />} />
      </Routes>
    </BrowserRouter>
  );
}
