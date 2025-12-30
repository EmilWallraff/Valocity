import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';

import { UserProvider } from './contexts/UserContext';

import Layout from './components/Layout';

import Home from './pages/Home';
import Impressum from './pages/Impressum';
import Rights from './pages/Rights';
import Datenschutz from './pages/Datenschutz';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import WinProbability from './pages/WinProbability';
import Weapons from './pages/Weapons';
import Agents from './pages/Agents';
import PlayerProfile from './pages/PlayerProfile';
import ProfileSearch from './pages/ProfileSearch';

import '@fontsource/inter/index.css';
import '@fontsource/rajdhani';



ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UserProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="impressum" element={<Impressum />} />
            <Route path="rights" element={<Rights />} />
            <Route path="datenschutz" element={<Datenschutz />} />
            <Route path="login" element={<Login />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="winprobability" element={<WinProbability />} />
            <Route path="weapons" element={<Weapons />} />
            <Route path="agents" element={<Agents />} />
            <Route path="playerprofile/:playername" element={<PlayerProfile />} />
            <Route path="profilesearch" element={<ProfileSearch />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </React.StrictMode>
);

