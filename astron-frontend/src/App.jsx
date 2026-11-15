import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import ExplorerPage from "./pages/ExplorerPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/explorer" element={<ExplorerPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;