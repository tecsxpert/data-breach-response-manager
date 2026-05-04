import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../services/api';

const DashboardPage = () => {
  const [stats, setStats] = useState({
    total: 0,
    critical: 0,
    investigating: 0,
    contained: 0
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, this would be a GET /api/stats
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/breaches/all');
        const breaches = response.data.content || response.data;
        
        // Calculate KPIs
        const total = breaches.length;
        const critical = breaches.filter(b => b.severity === 'Critical').length;
        const investigating = breaches.filter(b => b.status === 'Investigating').length;
        const contained = breaches.filter(b => b.status === 'Contained').length;
        
        setStats({ total, critical, investigating, contained });

        // Calculate chart data (group by severity)
        const severityCounts = { Low: 0, Medium: 0, High: 0, Critical: 0 };
        breaches.forEach(b => {
          if (severityCounts[b.severity] !== undefined) {
            severityCounts[b.severity]++;
          }
        });

        const formattedChartData = [
          { name: 'Low', count: severityCounts.Low, fill: '#3b82f6' },
          { name: 'Medium', count: severityCounts.Medium, fill: '#eab308' },
          { name: 'High', count: severityCounts.High, fill: '#f97316' },
          { name: 'Critical', count: severityCounts.Critical, fill: '#ef4444' }
        ];

        setChartData(formattedChartData);
      } catch (err) {
        console.error("Failed to load dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div className="p-8 text-center">Loading dashboard...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Overview Dashboard</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <h3 className="text-gray-500 text-sm font-semibold uppercase">Total Incidents</h3>
          <p className="text-3xl font-bold text-gray-800">{stats.total}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <h3 className="text-gray-500 text-sm font-semibold uppercase">Critical Severity</h3>
          <p className="text-3xl font-bold text-gray-800">{stats.critical}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <h3 className="text-gray-500 text-sm font-semibold uppercase">Currently Investigating</h3>
          <p className="text-3xl font-bold text-gray-800">{stats.investigating}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <h3 className="text-gray-500 text-sm font-semibold uppercase">Successfully Contained</h3>
          <p className="text-3xl font-bold text-gray-800">{stats.contained}</p>
        </div>
      </div>

      {/* Charts Area */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Incidents by Severity</h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Number of Breaches" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
