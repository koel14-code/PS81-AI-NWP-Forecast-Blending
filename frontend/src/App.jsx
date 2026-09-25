import React, { useState, useEffect } from 'react';
import './styles/theme.css';
import { api } from './api/client';
import { Layout } from './components/Layout';
import { Overview } from './pages/Overview';
import { ForecastIntelligence } from './pages/ForecastIntelligence';
import { AdaptiveWeights } from './pages/AdaptiveWeights';
import { SpatialIntelligence } from './pages/SpatialIntelligence';
import { Verification } from './pages/Verification';
import { ExtremeWeather } from './pages/ExtremeWeather';
import { Methodology } from './pages/Methodology';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  // Periodic backend health check
  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        if (isMounted) {
          setIsBackendOnline(res && res.status === 'online');
        }
      } catch (err) {
        console.error(`[SkyBlend Health Check Error] Target URL: ${api.getBaseUrl()}/api/health ->`, err.message);
        if (isMounted) {
          setIsBackendOnline(false);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <Overview onNavigate={(tab) => setActiveTab(tab)} />;
      case 'forecast': return <ForecastIntelligence />;
      case 'weights': return <AdaptiveWeights />;
      case 'spatial': return <SpatialIntelligence />;
      case 'verification': return <Verification />;
      case 'extreme': return <ExtremeWeather />;
      case 'methodology': return <Methodology />;
      default: return <Overview onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <Layout
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      isBackendOnline={isBackendOnline}
    >
      {renderContent()}
    </Layout>
  );
}

