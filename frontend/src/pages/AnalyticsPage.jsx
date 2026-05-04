import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';

const dummyData = {
  '30days': [
    { date: 'Apr 1', breaches: 2, affected: 5000 },
    { date: 'Apr 8', breaches: 5, affected: 12000 },
    { date: 'Apr 15', breaches: 1, affected: 300 },
    { date: 'Apr 22', breaches: 4, affected: 8000 },
    { date: 'Apr 29', breaches: 3, affected: 4500 }
  ],
  '90days': [
    { date: 'Feb', breaches: 12, affected: 45000 },
    { date: 'Mar', breaches: 8,  affected: 15000 },
    { date: 'Apr', breaches: 15, affected: 29800 }
  ],
  '1year': [
    { date: 'Q1', breaches: 25, affected: 150000 },
    { date: 'Q2', breaches: 18, affected: 85000 },
    { date: 'Q3', breaches: 30, affected: 210000 },
    { date: 'Q4', breaches: 22, affected: 115000 }
  ]
};

const AnalyticsPage = () => {
  const [period, setPeriod] = useState('30days');
  const data = dummyData[period];

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Breach Analytics</h1>
        
        {/* Period Selector (Day 10 Task) */}
        <div className="bg-white rounded-md shadow-sm border border-gray-200 p-1 flex">
          <button 
            className={`px-4 py-2 text-sm font-medium rounded-sm ${period === '30days' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setPeriod('30days')}
          >
            Last 30 Days
          </button>
          <button 
            className={`px-4 py-2 text-sm font-medium rounded-sm ${period === '90days' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setPeriod('90days')}
          >
            Last 90 Days
          </button>
          <button 
            className={`px-4 py-2 text-sm font-medium rounded-sm ${period === '1year' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setPeriod('1year')}
          >
            1 Year
          </button>
        </div>
      </div>

      <div className="space-y-8">
        {/* Trend Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-700">Breach Incident Trend</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="breaches" name="Incidents Reported" stroke="#3b82f6" strokeWidth={3} activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Impact Area Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-700">Affected Records Over Time</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorAffected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="affected" name="Exposed Records" stroke="#ef4444" fillOpacity={1} fill="url(#colorAffected)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
