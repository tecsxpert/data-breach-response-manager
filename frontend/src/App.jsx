import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import ListPage from './pages/ListPage';
import BreachFormPage from './pages/BreachFormPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DetailPage from './pages/DetailPage';
import AnalyticsPage from './pages/AnalyticsPage';

function NavBar() {
  const { user, logout } = useAuth();
  
  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-blue-600">DBRM</span>
            </Link>
            
            {user && (
              <div className="hidden sm:flex sm:space-x-8">
                <Link to="/" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300 text-sm font-medium">
                  List
                </Link>
                <Link to="/dashboard" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300 text-sm font-medium">
                  Dashboard
                </Link>
                <Link to="/analytics" className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300 text-sm font-medium">
                  Analytics
                </Link>
              </div>
            )}
          </div>
          <div className="flex items-center">
            {user ? (
              <button 
                onClick={logout}
                className="text-gray-600 hover:text-red-600 font-medium text-sm"
              >
                Logout ({user.username})
              </button>
            ) : (
              <Link to="/login" className="text-gray-600 hover:text-blue-600 font-medium text-sm">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100">
          <NavBar />
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              
              <Route path="/" element={<ProtectedRoute><ListPage /></ProtectedRoute>} />
              <Route path="/create" element={<ProtectedRoute><BreachFormPage /></ProtectedRoute>} />
              <Route path="/edit/:id" element={<ProtectedRoute><BreachFormPage /></ProtectedRoute>} />
              <Route path="/detail/:id" element={<ProtectedRoute><DetailPage /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
