import React from 'react'
import Sidebar from './Sidebar.jsx'

function Layout({ children }) {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        {children}
      </main>
    </div>
  )
}

export default Layout
