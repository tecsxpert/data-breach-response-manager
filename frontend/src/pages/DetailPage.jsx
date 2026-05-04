import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const DetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [breach, setBreach] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    const fetchBreach = async () => {
      try {
        const response = await api.get(`/api/breaches/${id}`);
        setBreach(response.data);
      } catch (err) {
        console.error("Failed to load breach details", err);
      } finally {
        setLoading(false);
      }
    };
    fetchBreach();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this record?")) {
      try {
        await api.delete(`/api/breaches/${id}`);
        navigate('/');
      } catch (err) {
        alert("Failed to delete record.");
      }
    }
  };

  const getScoreBadgeColor = (severity) => {
    switch (severity) {
      case 'Critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'High': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading details...</div>;
  if (!breach) return <div className="p-8 text-center text-red-500">Record not found.</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header section with Edit/Delete buttons */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">{breach.title}</h1>
          <div className="flex space-x-3 items-center">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getScoreBadgeColor(breach.severity)}`}>
              {breach.severity} Severity
            </span>
            <span className="text-gray-500 text-sm">Status: {breach.status}</span>
          </div>
        </div>
        <div className="flex space-x-3">
          <Link 
            to={`/edit/${id}`} 
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded border border-gray-300"
          >
            Edit
          </Link>
          <button 
            onClick={handleDelete}
            className="bg-red-50 hover:bg-red-100 text-red-600 font-semibold py-2 px-4 rounded border border-red-200"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">Description</h2>
            <p className="text-gray-600 whitespace-pre-line">{breach.description}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">Timeline & Impact</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Reported Date</p>
                <p className="font-medium text-gray-800">
                  {breach.reported_date ? new Date(breach.reported_date).toLocaleDateString() : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Incident Date</p>
                <p className="font-medium text-gray-800">
                  {breach.incident_date ? new Date(breach.incident_date).toLocaleDateString() : 'Unknown'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Affected Records</p>
                <p className="font-medium text-gray-800">
                  {breach.affected_records_count ? breach.affected_records_count.toLocaleString() : 'Estimating...'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* AI Panel (Day 8 Task) */}
        <div className="lg:col-span-1">
          <div className="bg-indigo-50 border border-indigo-100 rounded-lg shadow p-6 h-full flex flex-col">
            <div className="flex items-center mb-4 border-b border-indigo-200 pb-2">
              <svg className="w-5 h-5 text-indigo-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <h2 className="text-xl font-semibold text-indigo-900">AI Analysis</h2>
            </div>
            
            <div className="flex-grow flex flex-col space-y-4">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center py-10 space-y-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                  <p className="text-sm text-indigo-500">AI is analyzing the breach...</p>
                </div>
              ) : (
                <>
                  <div>
                    <h3 className="text-sm font-semibold text-indigo-800 mb-1">AI Summary</h3>
                    <p className="text-sm text-indigo-900 bg-white bg-opacity-60 p-3 rounded">
                      {breach.ai_summary || "No AI summary has been generated for this record yet."}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-indigo-800 mb-1">AI Recommendations</h3>
                    <p className="text-sm text-indigo-900 bg-white bg-opacity-60 p-3 rounded">
                      {breach.ai_recommendations || "Click the button below to generate response recommendations."}
                    </p>
                  </div>
                </>
              )}
            </div>
            
            <button 
              onClick={() => setAiLoading(true)}
              disabled={aiLoading}
              className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-2 px-4 rounded transition duration-150"
            >
              Generate AI Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailPage;
