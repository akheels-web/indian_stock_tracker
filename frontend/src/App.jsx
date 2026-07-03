import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import HomePage from './pages/HomePage.jsx'
import WatchlistPage from './pages/WatchlistPage.jsx'
import StockPage from './pages/StockPage.jsx'
import AlertsPage from './pages/AlertsPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/watchlist" element={<WatchlistPage />} />
        <Route path="/stock/:symbol" element={<StockPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
