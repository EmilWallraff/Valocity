import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';

import Layout from './components/Layout';
import ScrollToTop from './components/ScrollToTop';

import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import WinProbability from './pages/WinProbability';
import Weapons from './pages/Weapons';

import '@fontsource/inter/index.css';
import '@fontsource/rajdhani';



ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <ScrollToTop />
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="winprobability" element={<WinProbability />} />
        <Route path="weapons" element={<Weapons />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

