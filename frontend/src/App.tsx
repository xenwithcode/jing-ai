import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import LandingPage from './pages/LandingPage';
import ArchitecturePage from './pages/ArchitecturePage';
import BlogPage from './pages/BlogPage';
import BenchmarkPage from './pages/BenchmarkPage';
import DemoPage from './pages/DemoPage';
import DashboardPage from './pages/DashboardPage';
import AppPage from './AppPage';

function App() {
  return (
    <Router>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
        <Route path="/blog" element={<BlogPage />} />
        <Route path="/benchmark" element={<BenchmarkPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="/app" element={<AppPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </Router>
  );
}

export default App;
